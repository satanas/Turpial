$(document).ready(function() {
    var column_width = window.innerWidth - 12;
    $('#notice').css('width', column_width + 'px');
    $('#user').focus();
    $('#passwd').hide();
    $('#lbl-passwd').hide();
    $('#user').hide();
    $('#lbl-user').hide();
    $("#protocol").change(function() {
        check_protocol();
    });
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
    alert("uno")
    block_account_controls(true);
    var user = $('#user').val();
    var passwd = $('#passwd').val();
    var protocol = $('#protocol').val();
    
    if (protocol == 'null') {
        block_account_controls(false);
        show_notice("<% $fields_cant_be_empty %>", 'error');
        return false;
    }
    
    if ((passwd == '' || user == '') && (protocol == 'identica')) {
        block_account_controls(false);
        show_notice("<% $fields_cant_be_empty %>", 'error');
        return false;
    }
    
    exec_command('cmd:save_account:' + user + '-%&%-' + protocol + '-%&%-' + passwd);

}

function cancel_login(message) {
    block_account_controls(false);
    show_notice(message, 'error');
}

function set_loading_message(message) {
    $('#loading-msg').html(message);
}

function check_protocol() {
    var protocol = $('#protocol').val();
    if (protocol == 'twitter' || protocol == 'null') {
        $('#passwd').hide();
        $('#lbl-passwd').hide();
        $('#user').hide();
        $('#lbl-user').hide();
    } else {
        $('#passwd').show();
        $('#lbl-passwd').show();
        $('#user').show();
        $('#lbl-user').show();
    }
}
