const displayAlert = (message, tag = "info") => {
    if (tag === 'error'){
        tag = 'danger'
    }
    let alertDiv = `<div class="alert alert-${tag}" id="page-alert" style="display: none;">
                    <strong>${message}</strong>
                    <a href="#" class="close" data-dismiss="alert">&times;</a>
                    </div>`;
    $(alertDiv).appendTo($('.nav-breadcrumbs-alert')).slideDown(100);
};

const renderAlerts = (messages) => {
    for (let message of messages) {
        displayAlert(message.message, message.level_tag);
    }
};
