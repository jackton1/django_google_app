from __future__ import absolute_import

import json
import logging
import os
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
try:
    from functools import lru_cache
except ImportError:
    from repoze.lru import lru_cache
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.shortcuts import get_object_or_404
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client
from oauth2client.contrib import xsrfutil
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from .models import UserTokens, CredentialsModel

log = logging.getLogger(__name__)


def _build_service(http, service_name='fusiontables', version='v1'):
    return build(service_name, version, http=http,
                 developerKey=settings.GOOGLE_FUSION_TABLE_API_KEY)


def store_user_tokens(user, access_token, refresh_token):
    return UserTokens.objects.get_or_create(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@contextmanager
def verify_client_id_json(filename):
    """
    Verify the required client_id.json values are set.
    
    A context manager to parse the client_id.json and set the missing
    values with the env vars.
    :param filename: Client id json filename.
    :type filename: str
    """
    if not os.path.exists(filename):
        raise OSError('Path specified doesn\'t exists: ' + filename)
    fp = open(filename)
    client_id = json.load(fp)
    required_keys = ['client_id', 'project_id',
                     'client_secret']
    for k in required_keys:
        if client_id['web'][k] == '':
            env_var = k.upper()
            if not os.environ.get(env_var):
                raise ValueError("Client ID json required key value"
                                 " not set in {} or missing env var {}"
                                 .format(filename, env_var))
            else:
                client_id['web'][k] = os.environ.get(env_var)
    f = NamedTemporaryFile(mode='w', dir=os.path.dirname(filename),
                           suffix='.json', delete=False)
    json.dump(client_id, f)
    f.seek(0)
    f.close()
    try:
        yield f.name
    finally:
        try:
            os.unlink(f.name)
        except OSError:
            pass


class FlowClient(object):
    """
    FlowClient to manage credentials.
    """
    def __init__(self,
                 request,
                 client_secret_json=settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
                 scope=settings.FUSION_TABLE_SCOPE,
                 redirect_url=settings.OAUTH2_CLIENT_REDIRECT_PATH,
                 ):
        with verify_client_id_json(client_secret_json) as client_secret:
            self.flow = client.flow_from_clientsecrets(
                    filename=client_secret,
                    scope=scope,
                    redirect_uri=redirect_url)
        self.request = request
        self.user = self.request.user
        self.http = Http()

    def get_credential(self):
        # Read credentials
        storage = DjangoORMStorage(
            CredentialsModel, 'id', self.user, 'credential')
        return storage.get()

    def generate_token(self):
        token = xsrfutil.generate_token(
            settings.CLIENT_SECRET, self.user.id)
        self.flow.params['state'] = token
        return token

    def update_user_token_model(self, token, authorization_url):
        user_token = UserTokens(user=self.user,
                                access_token=token,
                                authorized_url=authorization_url)
        user_token.save()

    def credential_is_valid(self):
        credential = self.get_credential()
        # Credential not valid if None or credential.invalid == True
        if credential:
            return not credential.access_token_expired
        return False

    def get_authorization_url(self):
        if not self.credential_is_valid():
            token = self.generate_token()
            authorization_url = self.flow.step1_get_authorize_url()
            self.update_user_token_model(token, authorization_url)
            return authorization_url

    def get_user_token(self):
        user_token = get_object_or_404(UserTokens, pk=self.user.id)
        return user_token.access_token

    def update_user_credential(self):
        # Create credential
        request = self.request
        credential = self.flow.step2_exchange(request.GET)
        storage = DjangoORMStorage(CredentialsModel, 'id',
                                   request.user, 'credential')
        # Write credential
        storage.put(credential)
        cred, created = CredentialsModel.objects.update_or_create(
            id=request.user, credential=credential)
        return cred, created

    def _authorize_http(self):
        if self.credential_is_valid():
            credential = self.get_credential()
            self.http = credential.authorize(self.http)

    @lru_cache(maxsize=None)
    def get_service_and_table_id(self):
        self._authorize_http()
        # http is authorized with the user's Credentials and can be
        # used in API calls
        table_id = settings.FUSION_TABLE_ID
        service = _build_service(self.http)
        return service, table_id


class FusionTableMixin(object):
    """
    Mixin to manage Interactions with google fusion table.
    """
    __metaclass__ = ABCMeta

    @staticmethod
    def select_all_rows(service, table_id):
        return (service.query()
                .sql(sql='SELECT ROWID, address,'
                         ' latitude, longitude,'
                         ' computed_address FROM %s'
                         % table_id).execute())

    @staticmethod
    def select_all_addresses(service, table_id):
        return (service.query()
                .sql(sql='SELECT address FROM %s'
                         % table_id).execute())

    @staticmethod
    def delete_all_addresses(service, table_id):
        return service.query().sql(
            sql='DELETE FROM %s;' % table_id).execute()

    @staticmethod
    def delete_address_at_row(service, table_id, row_id):
        return (
            service.query()
            .sql(sql='DELETE FROM %s WHERE ROWID = %d' % (table_id, row_id,))
            .execute())

    @classmethod
    def bulk_delete(cls, results, service, table_id):
        delete_query = 'DELETE FROM %s WHERE ROWID IN ({row_ids});' % table_id
        row_ids = [row.get('rowid') for row in results]

        return (service.query()
                .sql(sql=delete_query.format(row_ids=row_ids))
                .execute())

    @classmethod
    def bulk_save(cls, addresses, service, table_id):
        # limit insert to 60 rows
        for query in list(cls.generate_values(addresses, table_id))[:60]:
            service.query().sql(sql=query).execute()

    @classmethod
    def generate_values(cls, addresses, table_id):
        values_dict = {'table_id': table_id}
        insert_query = ("INSERT INTO {table_id} "
                        "(address, latitude, longitude,"
                        " computed_address) VALUES "
                        "\"('{address}', {latitude},"
                        " {longitude}, '{computed_address}')\"")
        for address in addresses:
            values_dict.update(cls.address_model_to_dict(address))
            yield insert_query.format(**values_dict)

    @classmethod
    def get_style(cls, service, table_id, style_id=1):
        style = (service.style()
                 .get(tableId=table_id,
                      styleId=style_id)
                 .execute()) or {}
        return json.dumps(style)

    @classmethod
    def save(cls, address, service, table_id):
        values_dict = cls.address_model_to_dict(address)
        values_dict.update({'table_id': table_id})
        if not cls.address_exists(address, service, table_id):
            return (service.query()
                    .sql(sql="INSERT INTO {table_id} "
                             "(address, latitude, longitude,"
                             " computed_address)"
                             "VALUES \"('{address}', {latitude}, "
                             "{longitude}, '{computed_address}')\""
                         .format(**values_dict)).execute())
        else:
            log.debug("Saving already existing address.")

    @classmethod
    def address_exists(cls, address, service, table_id):
        query_dict = {'table_id': table_id,
                      'address': address.address}
        results = (service.query()
                   .sql(sql="SELECT address FROM {table_id} "
                            "WHERE address LIKE '%{address}%'"
                        .format(**query_dict)).execute())
        try:
            return next(cls._process_result(results))
        except StopIteration:
            pass
        return None

    @classmethod
    @abstractmethod
    def get_service_and_table_id(cls):
        # This should be removed.
        # http = get_http_auth(settings.GOOGLE_SERVICE_ACCOUNT_KEY_FILE)
        # http is authorized with the user's Credentials and can be
        # used in API calls
        # table_id = settings.FUSION_TABLE_ID
        # service = _build_service(http)
        # return service, table_id
        pass

    @staticmethod
    def get_columns(results):
        return results.get('columns', [])

    @classmethod
    def _process_result(cls, results, columns=None, excludes=None):
        rows = results.get('rows', [])
        columns = columns or cls.get_columns(results)
        for row in rows:
            ret_dict = dict(zip(columns, row))
            if excludes:
                for key in excludes:
                    if key in ret_dict:
                        del ret_dict[key]
            yield ret_dict

    @classmethod
    def address_model_to_dict(cls, address):
        """
        Convert the ``map_app.models.Address`` instance to a dict.

        :param address: The address model instance.
        :type address: ``map_app.models.Address``
        :rtype: dict
        """
        keys = ['address', 'latitude', 'longitude', 'computed_address']
        values_dict = {}
        for key in keys:
            try:
                values_dict[key] = getattr(address, key, '') or ''
            except AttributeError:
                values_dict[key] = address.get(key, '')
        return values_dict
