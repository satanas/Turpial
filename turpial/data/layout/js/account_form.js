$(document).ready(function() {
    var column_width = window.innerWidth - 12;
    $('#notice').css('width', column_width + 'px');
});

function block_account_controls(block) {
    var user = $('#user');
    var passwd = $('#passwd');
    var protocol = $('#protocol');
    var acc_options = $('#account_options');
    var acc_loading = $('#account-loading');
    
    if (block == true) {
        acc_options.hide();
        acc_loading.show();
        user.attr('disabled', 'disabled');
        passwd.attr('disabled', 'disabled');
        protocol.attr('disabled', 'disabled');
    } else {
        acc_options.show();
        acc_loading.hide();
        user.removeAttr('disabled');
        passwd.removeAttr('disabled');
        protocol.removeAttr('disabled');
    }
}

function save_account() {
    block_account_controls(true);
    var user = $('#user').val();
    var passwd = $('#passwd').val();
    var protocol = $('#protocol').val();
    
    if ((user == '') || (passwd == '') || (protocol == 'null')) {
        block_account_controls(false);
        show_notice("<% $fields_cant_be_empty %>", 'error');
        return false;
    }
    
    window.location = 'cmd:save_account:' + user + '-%&%-' + protocol + '-%&%-' + passwd;
}

function cancel_login(message) {
    block_account_controls(false);
    show_notice(message, 'error');
}
