login_started = false;

$(document).ready(function() {
    $('.account').each(function() {
        var id = $(this).attr('id');
        $(this).mouseover(function() {
            if (login_started == false) {
                $('#' + id + '-options').show();
            }
        }).mouseout(function() {
            $('#' + id + '-options').hide();
        });
    });
    
    $('#notice').click(function() {
        hide_notice();
    });
});

function show_account_dialog(us, pw, pt, rem) {
    $('#dialog').show();
    $('.tab').show();
    $('#modal').fadeIn();
    
    var user = $('#user');
    var passwd = $('#passwd');
    var protocol = $('#protocol');
    var remember = $('#remember');
    
    if (us == undefined) {
        user.val('');
        user.removeAttr('disabled');
        user.focus();
    } else {
        user.val(us);
        user.attr('disabled', 'disabled');
        passwd.focus();
    }
    
    if (pw == undefined)
        passwd.val('');
    else
        passwd.val(pw);
    
    if (pt == undefined) {
        protocol.val('twitter');
        protocol.removeAttr('disabled');
    } else {
        protocol.val(pt);
        protocol.attr('disabled', 'disabled');
    }
    
    if (rem == undefined)
        remember.attr('checked', false);
    else
        remember.attr('checked', rem);
}

function close_account_dialog() {
    $('#modal').fadeOut();
    $('#dialog').hide();
    $('.tab').hide();
    hide_notice();
}

function block_account_controls(block) {
    var user = $('#user');
    var passwd = $('#passwd');
    var protocol = $('#protocol');
    var remember = $('#remember');
    var acc_options = $('#account_options');
    var acc_loading = $('#account-loading');
    
    if (block == true) {
        acc_options.hide();
        acc_loading.show();
        user.attr('disabled', 'disabled');
        passwd.attr('disabled', 'disabled');
        protocol.attr('disabled', 'disabled');
        remember.attr('disabled', 'disabled');
    } else {
        acc_options.show();
        acc_loading.hide();
        user.removeAttr('disabled');
        passwd.removeAttr('disabled');
        protocol.removeAttr('disabled');
        remember.removeAttr('disabled');
    }
}

function block_login_controls(block) {
    var button = $('#login-button');
    var loader = $('#login-loading');
    var nav = $('#nav');
    var bnav = $('#blocked-nav');
    login_started = block;
    
    if (block == true) {
        button.hide();
        nav.hide();
        bnav.show();
        loader.show();
    } else {
        button.show();
        nav.show();
        bnav.hide();
        loader.hide();
    }
    
    $('input[type=checkbox]').each(function() {
        if (block == true) {
            $(this).attr('disabled', 'disabled');
        } else {
            $(this).removeAttr('disabled');
        }
    });
    
    $('.account label').each(function() {
        if (block == true) {
            $(this).addClass('disabled_text');
        } else {
            $(this).removeClass('disabled_text');
        }
    });
    
    $('.options label').each(function() {
        if (block == true) {
            $(this).addClass('disabled_text');
        } else {
            $(this).removeClass('disabled_text');
        }
    });
}

function save_account() {
    block_account_controls(true);
    var user = $('#user').val();
    var passwd = $('#passwd').val();
    var protocol = $('#protocol').val();
    var remember = $('#remember').is(':checked');
    
    if ((user == '') || (passwd == '')) {
        block_account_controls(false);
        show_notice("<% $fields_cant_be_empty %>", 'error');
        return false;
    }
    
    window.location = 'cmd:save_account:' + user + '\0' + passwd+ '\0' + protocol+ '\0' + remember;
}

function delete_account(acc) {
    var rtn = confirm('Delete account ' + acc);
    if (rtn == true)
        window.location = 'cmd:delete_account:' + acc
}

function login() {
    block_login_controls(true);
    var accounts = ''
    $('.account input[type=checkbox]').each(function() {
        var checked = $(this).attr('checked');
        if (checked == 'checked') {
            accounts += $(this).val() + '\0';
        }
    });
    
    if (accounts == '') {
        block_login_controls(false);
        show_notice("<% $one_account_to_login %>", 'error');
        return false;
    }
    
    window.location = 'cmd:login:' + accounts;
}

function show_notice(message, type) {
    $('#notice').html(message);
    $('#notice').addClass(type);
    $('#notice').show();
    setTimeout(hide_notice, 5000);
}

function hide_notice() {
    $('#notice').hide();
    $('#notice').html('');
    $('#notice').removeClass('error');
    $('#notice').removeClass('info');
}
