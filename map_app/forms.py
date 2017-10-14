from __future__ import absolute_import, unicode_literals

import logging

from django import forms
from django.contrib import messages
from django.utils.encoding import smart_str
from easy_maps.models import Address

from map_app.exceptions import RequestNotFoundException
from . import lib

log = logging.getLogger(__name__)


class AddressForm(forms.ModelForm):
    address = forms.CharField(max_length=255, required=True)

    class Meta:
        model = Address
        fields = ['address']

    def _post_clean(self):
        super(AddressForm, self)._post_clean()
        if self.cleaned_data.get('address'):
            q = Address.objects.filter(
                address__icontains=self.cleaned_data['address']
            ).exists()
            if q:
                message_ = "The %s could not be %s because similar address already exists." % (
                        self.instance.__class__.__name__, 'created'
                    )
                log.debug("%s : %s" % (message_, self.cleaned_data['address']))
                self._update_errors(message_)

    def save(self, commit=True, request=None):
        log.info("Saving new address")
        try:
            instance = super(AddressForm, self).save(commit=commit)
        except ValueError as e:
            log.debug(smart_str(e))
            messages.error(request, smart_str(e))
        else:
            if instance and not self._valid_address(instance):
                message_ = ('Geocode error occurred saving %s: %s' %
                            (instance.__class__.__name__, instance.address,))
                messages.error(request, message_)
                instance.delete()
                return
            log.info("Adding address to fusion table.")
            if not request or not request.user:
                message_ = "Request or user required objects not found."
                log.error(message_)
                raise RequestNotFoundException(message_)
            else:
                flow = lib.FlowClient(request)
                service, table_id = flow.get_service_and_table_id()
                fusion_table_addresses = lib.FusionTableMixin.address_exists(
                        instance, service, table_id)
                added_to_fusion_table = False
                if fusion_table_addresses is not None:
                    log.debug("Address already exist in fusion table:"
                              " %s" % (instance.address,))
                else:
                    log.info("Adding address to fusion table : %s"
                             % instance.address)
                    added_to_fusion_table = True
                    lib.FusionTableMixin.save(instance, service, table_id)

                if instance:
                    part = "Successfully added a new "
                    message_ = "%s %s: %s" % (
                            part,
                            instance.__class__.__name__,
                            instance.address
                        )
                    if added_to_fusion_table:
                        f_part = part + "%s to fusion table: %s"
                        f_message_ = f_part % (
                            instance.__class__.__name__,
                            instance.address
                        )
                        log.info(f_message_)
                    messages.success(request, message_)
                    log.info(message_)
            return instance

    def _valid_address(self, instance):
        if instance.geocode_error or not instance.computed_address:
            message_ = 'Geocode Error'
            log.debug("%s : %s" % (smart_str(str(message_)),
                                   self.cleaned_data['address']))
            self._update_errors(message_)
            return False
        return True

    @staticmethod
    def get_addresses():
        return Address.objects.only('address').order_by('-id').all()
