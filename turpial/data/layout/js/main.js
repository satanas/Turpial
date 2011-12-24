var arg_sep = '<% @arg_sep %>';
var maxcharlimit = 140;
var num_columns = <% @num_columns %>;

$(document).ready(function() {
    recalculate_column_size();
    $('#alert-message').click(function() {
        hide_notice();
    });
    $(window).resize(function() {
        recalculate_column_size();
    });
    enable_key_events();
});

function recalculate_column_size(nw, nh) {
    var width = window.innerWidth;
    var height = window.innerHeight;
    if (nw != undefined)
        width = nw;
    if (nh != undefined)
        height = nh;
    
    var content_height = height - 23;
    var column_width = (width / num_columns) - 1;
    var column_height = content_height;
    var wrapper_height = height - 32;
    var list_width = column_width - 11;
    var list_height = column_height - 35;
    var combo_width = column_width - 60;
    var tweet_width = column_width - 92;
    var update_msg_width = width - 12;
    
    var alert_msg_width = width - 60;
    var alert_msg_left = 20;
    var alert_lbl_width = alert_msg_width - 35;
    
    var profile_win_left = (width - 290) / 2;
    
    $('#content').css('height', content_height + 'px');
    $('.column').css('width', column_width + 'px');
    $('.column').css('height', column_height + 'px');
    $('.wrapper').css('height', wrapper_height + 'px');
    $('.wrapper').css('width', column_width + 'px');
    
    $('.list').css('height', list_height + 'px');
    $('.list').css('width', list_width + 'px');
    $('.combo').css('width', combo_width + 'px');
    $('.tweet .content').css('width', tweet_width + 'px');
    
    $('.message-container').css('width', update_msg_width + 'px');
    
    $('#alert-message').css('width', alert_msg_width + 'px');
    $('#alert-message').css('left', alert_msg_left + 'px');
    $('#alert-label').css('width', alert_lbl_width + 'px');
    
    $('#profile-window').css('left', profile_win_left + 'px');
}

function change_num_columns(num) {
    num_columns = num;
}

function add_column() {
    num_columns++;
    recalculate_column_size();
}

function remove_column(column_id) {
    $('#column-' + column_id).remove();
    num_columns--;
    recalculate_column_size();
}

function reset_column(column_id) {
    $('#list-' + column_id).animate({scrollTop : 0},1000);
}

function enable_trigger() {
    $('.content').mouseover(function() {
        var name = $(this).attr('name');
        var indicator = $('#indicator-' + name).val();
        if (indicator != "") return;
        $('#buttonbox-' + name).show();
        $('.favmark-' + name).show();
    });
    
    $('.content').mouseleave(function() {
        var name = $(this).attr('name');
        $('#buttonbox-' + name).hide();
        $('.favmark-' + name).hide();
    });
}

function enable_key_events() {
    $('#update-message').keyup(function(event) {
        //console.log('tecla: ' + event.keyCode);
        if (event.keyCode == 27) {
            close_update_box();
            return;
        }
        count_chars();
    });
}

function show_update_box(message, status_id, account_id, title) {
    $('#modal').fadeIn();
    $('#update-box').fadeIn();
    
    
    if (title == undefined) {
        $('#update-box-title').html("<% $whats_happening %>");
    } else {
        $('#update-box-title').html(title);
    }
    
    if (message != undefined) {
        $('#update-message').focus().val(message);
        count_chars();
    }
    
    $('#update-message').focus();
    
    if (status_id != undefined) {
        $('#in-reply-to-id').val(status_id);
        $('.acc_selector').each(function() {
            $(this).attr('disabled', 'disabled');
            $(this).attr('checked', false);
        });
        $('#acc-selector-' + account_id).attr('checked', true);
    }
}

function close_update_box() {
    var status = $('#update-box').attr('name');
    if (status != '') return;
    hide_notice();
    $('#update-box').fadeOut(400, reset_update_box);
    $('#modal').fadeOut(400);
}

function done_update_box(recalculate) {
    $('#update-box').attr('name', '');
    if ((recalculate != undefined) && (recalculate == true)) {
        recalculate_column_size();
        enable_trigger();
    }
    close_update_box();
}

function reset_update_box() {
    $('#update-message').val('');
    $('#in-reply-to-id').val('');
    $('#char-counter').html('140');
    $('#char-counter').removeClass('maxchar');
    unlock_update_box();
}

function update_status_error(message) {
    $('#update-box').attr('name', '');
    show_notice(message, 'error');
    unlock_update_box();
}

function broadcast_status_error(good_accounts, message) {
    $('#update-box').attr('name', '');
    show_notice(message, 'error');
    unlock_update_box();
    for (var i=0; i < good_accounts.length; i++) {
        var acc = good_accounts[i];
        $('#acc-selector-' + acc).attr('disabled', 'disabled');
        $('#acc-selector-' + acc).attr('checked', false);
    }
}

function lock_update_box(message) {
    $('#update-box').attr('name', message);
    $('#update-message').attr('disabled', 'disabled');
    $('.acc_selector').each(function() {
        $(this).attr('disabled', 'disabled');
    });
    $('#buttonbox-update').hide();
    $('#progress-box-updatebox').show();
    $('#progress-msg-updatebox').html(message);
}

function unlock_update_box() {
    $('#update-message').removeAttr('disabled');
    $('.acc_selector').each(function() {
        $(this).removeAttr('disabled');
    });
    $('#progress-box-updatebox').hide();
    $('#progress-msg-updatebox').html('');
    $('#buttonbox-update').show();
}

function count_chars() {
    var count = maxcharlimit - $('#update-message').val().length;
    $('#char-counter').html(count);
    if (count < 10) {
        $('#char-counter').addClass('maxchar');
    } else {
        $('#char-counter').removeClass('maxchar');
    }
}

function lock_status(status_id, message) {
    $('#buttonbox-' + status_id).hide();
    $('.favmark-' + status_id).hide();
    $('#progress-box-' + status_id).show();
    $('#progress-msg-' + status_id).html(message);
    $('#indicator-' + status_id).val(message);
}

function unlock_status(status_id) {
    $('#progress-box-' + status_id).fadeOut(400, function() {
        $('#progress-msg-' + status_id).html('');
        $('#indicator-' + status_id).val('');
    });
}

function update_favorite_mark(status_id, cmd, label, visible) {
    $('#fav-mark-' + status_id).attr('href', cmd);
    $('#fav-mark-' + status_id).html(label);
    if (visible == true)
        $('#fav-icon-' + status_id).show();
    else
        $('#fav-icon-' + status_id).hide();
}

function update_retweeted_mark(status_id, visible) {
    if (visible == true)
        $('#retweeted-icon-' + status_id).show();
    else
        $('#retweeted-icon-' + status_id).hide();
}

function delete_status(status_id) {
    $('#' + status_id).remove();
}

function show_profile_window(account_id, username) {
    $('#modal').fadeIn();
    $('#profile-window').fadeIn();
    $('#progress-box-profile-window').fadeIn();
    exec_command('cmd:show_profile:' + account_id + arg_sep + username);
    
}

function update_profile_window(profile) {
    $('#progress-box-profile-window').hide();
    $('#profile-window-content').html(profile);
}

function profile_window_error(message) {
    $('#progress-box-profile-window').hide();
    show_notice(message, 'error');
}

function close_profile_window() {
    var status = $('#profile-window').attr('name');
    if (status != '') return;
    hide_notice();
    $('#profile-window').fadeOut(400, reset_profile_window);
    $('#modal').fadeOut(400);
}

function reset_profile_window() {
    $('#profile-window-content').html('');
}

/* Callbacks */

function start_updating_column(column_id) {
    $('#header-buttons-' + column_id).hide();
    $('#header-progress-' + column_id).show();
}

function stop_updating_column(column_id) {
    $('#header-buttons-' + column_id).show();
    $('#header-progress-' + column_id).hide();
    recalculate_column_size();
    enable_trigger();
}

function append_status_to_timeline(account_id, html_status) {
    $('#list-' + account_id + '-timeline').prepend(html_status);
    recalculate_column_size();
    enable_trigger();
}

/* Commands */

function update_status() {
    var selected = '';
    var in_reply_to_id = $('#in-reply-to-id').val();
    var text = $('#update-message').val();
    $('.acc_selector').each(function() {
        if ($(this).attr('checked'))
            if (selected == '')
                selected = $(this).val();
            else
                selected += '|' + $(this).val();
    });
    
    if (selected != '') {
        if (text == '') {
            show_notice('<% $you_must_write_something %>', 'warning');
        } else if (text.length > maxcharlimit) {
            show_notice('<% $message_like_testament %>', 'warning');
        } else {
            lock_update_box('<% $updating_status %>');
            if (in_reply_to_id == ''){
                exec_command('cmd:update_status:' + selected + arg_sep + packstr(text));
            } else {
                exec_command('cmd:reply_status:' + selected + arg_sep + in_reply_to_id + arg_sep + packstr(text));
            }
        }
    } else {
        show_notice('<% $select_account_to_post %>', 'warning');
    }
}

function quote_status(account_id, username, text) {
    console.log(account_id + ',' + username + ',' + text);
    var rt = "RT @" + username + ": " + text;
    show_update_box(rt);
}

function reply_status(account_id, status_id, title, mentions) {
    console.log(account_id + ',' + status_id + ',' + mentions);
    var msg = "";
    for (var i=0; i < mentions.length; i++) {
        msg += "@" + mentions[i] + " ";
    }
    show_update_box(msg, status_id, account_id, title);
}
