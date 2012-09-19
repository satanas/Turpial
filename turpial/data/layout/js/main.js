var ARG_SEP = '<% @arg_sep %>';
var MAXCHARLIMIT = 140;
var NUM_COLUMNS = <% @num_columns %>;
var FRIENDS = [];
var IMAGEVIEW_W;
var IMAGEVIEW_H;
var TURPIAL_ALL_SEQ = '38384040373937396665';
var CURR_SEQ = '';
var CTRL_PRESSED = false;
//var SCROLLBAR_WIDTH = 23;
var MIN_COLUMN_SIZE = 250
var COLUMN_OFFSET = 0
var VISIBLE_COLUMNS = 1

// Shortcuts
var lKey = 76;

$(document).ready(function() {
    recalculate_column_size();
    $('#alert-message').click(function() {
        hide_notice();
    });
    $('a').live('click', (function(){
        this.blur();
    }));
    $(window).resize(function() {
        recalculate_column_size();
    });
    enable_key_events();
    enable_click_events()

});

function recalculate_column_size(nw, nh) {
    var width = window.innerWidth; // $(window).width();
    var height = window.innerHeight; // $(window).height();
    if (nw != undefined)
        width = nw;
    if (nh != undefined)
        height = nh;

    autoadjust_size();

    var column_width = Math.floor(width / VISIBLE_COLUMNS) - 2;
    var column_height = height - 25;
    var list_width = column_width - 10; // margin 2 x 5px
    var list_height = column_height - 35;
    var combo_width = column_width - 100;
    var tweet_width = column_width - 85;
    var update_msg_width = width - 12;

    var alert_msg_width = width - 60;
    var alert_msg_left = 20;
    var alert_lbl_width = alert_msg_width - 35;

    var profile_win_left = Math.floor((width - 290) / 2);
    var autocomplete_win_left = Math.floor((width - 200) / 2);

    $('.column').css('width', column_width + 'px');
    $('.list').css('height', list_height + 'px');
    $('.list').css('width', list_width + 'px');
    $('.header-label').css('width', combo_width + 'px');
    $('.tweet .content').css('width', tweet_width + 'px');
    $('.message-container').css('width', update_msg_width + 'px');

    $('#alert-message').css('width', alert_msg_width + 'px');
    $('#alert-message').css('left', alert_msg_left + 'px');
    $('#alert-label').css('width', alert_lbl_width + 'px');

    $('#profile-window').css('left', profile_win_left + 'px');
    $('#confirm-window').css('left', profile_win_left + 'px');
    $('#autocomplete-window').css('left', autocomplete_win_left + 'px');
}

function change_num_columns(num) {
    NUM_COLUMNS = num;
}

function match_pattern(pattern) {
  if (pattern == CURR_SEQ) {
    CURR_SEQ = '';
    return 1;
  }

  match = pattern.substr(0, CURR_SEQ.length);
  if (match != CURR_SEQ) {
    return -1;
  } else {
    return 0;
  }
}

function check_patterns() {
  if (match_pattern(TURPIAL_ALL_SEQ) == 1) {
    exec_command('cmd:turpial_all');
    return;
  } else if (match_pattern(TURPIAL_ALL_SEQ) == 0) {
    return;
  }
  CURR_SEQ = '';
}

function enable_trigger() {
    $('.tweet').on( "mouseover", function() {
        var indicator = $(this).children('input:first').val();
        if (indicator != "") return;
        $(this).children('.options').children(':nth-child(1)').show();
        $(this).find('div[name="fav-icon"]').show();
    });

    $('.tweet').on("mouseleave", function() {
        $(this).children('.options').children(':nth-child(1)').hide();
        $(this).find('div[name="fav-icon"]').hide();
    });
}

function enable_key_events() {
    $('#update-message').keyup(function(e) {
        count_chars();
    });


    $('#update-message').keydown(function(e) {
        if (e.keyCode == 27) {
            close_update_box();
            e.stopPropagation();
            return;
        } else if (e.keyCode == 13) {
            /* TODO: Submit with Enter */
            console.log('submit with enter');
            e.stopPropagation();
            return;
        }
    });

    /* Activate autocomplete dialog */
    $('#update-message').keypress(function(event) {
        if (event.which == 64) {
            event.stopPropagation();
            var index = $(this).getCursorPosition();
            var text = $('#update-message').val();
            if (index == 0) {
                show_autocomplete_for_status(index);
            } else {
                var prev = text.substr(index - 1, 1);
                if (prev == ' ') {
                    show_autocomplete_for_status(index);
                }
            }
            return;
        }
    });

    $('#autocomplete-username').keyup(function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (e.keyCode == 27) {
            close_autocomplete_window();
        } else if (CTRL_PRESSED && e.keyCode == lKey) {
            load_friends();
        } else if (e.keyCode == 13) {
            eval($('#autocomplete-add-function').val());
        }
    });

    $(window).keyup(function(e) {
        CURR_SEQ = CURR_SEQ + e.keyCode;
        check_patterns();

        // Handle the ctrl key release event
        if (e.keyCode == 17) CTRL_PRESSED = false;
    });

    $(window).keydown(function(e) {
        // Handle the ctrl key press event
        if (e.keyCode == 17) CTRL_PRESSED = true;
    });

}

function enable_click_events() {
    $('#show-profile-details-action').click(function(){
        $('#profile-statuses').hide()
        $('#profile-details').show()
    })

    $('#show-profile-statuses-action').click(function(){
        $('#profile-details').hide()
        $('#profile-statuses').show()
    })
}

function autoadjust_size() {
    var width = window.innerWidth
    VISIBLE_COLUMNS = parseInt(width / MIN_COLUMN_SIZE)
    if (VISIBLE_COLUMNS > NUM_COLUMNS)
        VISIBLE_COLUMNS = NUM_COLUMNS

    $('#content thead tr td').show()
    $('#content tbody tr td').show()
    for (var i = NUM_COLUMNS; i > VISIBLE_COLUMNS; i--) {
        $('#content thead tr td:nth-child(' + i + ')').hide()
        $('#content tbody tr td:nth-child(' + i + ')').hide()
    }
}

/* Columns */

function add_column(header, column) {
    $('#headers').append(header);
    $('#columns').append(column);
    NUM_COLUMNS++;
    recalculate_column_size();
}

function remove_column(column_id) {
    $('#column-' + column_id).remove();
    $('#header-' + column_id).remove();
    NUM_COLUMNS--;
    recalculate_column_size();
}

function reset_column(column_id) {
    $('#list-' + column_id).animate({scrollTop : 0},1000);
}

function update_column(column_id, statuses) {
    stop_updating_column(column_id);
}

/* Modality */

/* This method should be called when something in the profile window can
break the modal layout */
function close_modal_dialogs() {
}

/* Updatebox */

function show_update_box(message, status_id, account_id, title) {
    $('#modal').fadeIn();
    $('#update-box').fadeIn();
    $('#upload-img-cmd').show();
    $('#direct-message-to').val('');

    if (title == undefined) {
        $('#update-box-title').html("<% $whats_happening %>");
    } else {
        $('#update-box-title').html(title);
    }

    if (message != undefined) {
        console.log('message ' + message);
        $('#update-message').focus().val(message);
        count_chars();
    }

    if (status_id != undefined) {
        $('#in-reply-to-id').val(status_id);
        $('.acc_selector').each(function() {
            $(this).attr('disabled', 'disabled');
            $(this).attr('checked', false);
        });
        $('#acc-selector-' + account_id).attr('checked', true);
    }

    $('#update-message').focus();
    if ((message != undefined) && (status_id == undefined) && (account_id == undefined)) {
        $('#update-message').setCursorPosition(0);
    }
}

function show_update_box_for_direct(account_id, username) {
    $('#modal').fadeIn();
    $('#update-box').fadeIn();
    $('#upload-img-cmd').hide();
    $('#update-box-title').html("<% $send_message_to %> " + username);
    $('#direct-message-to').val(username);
    $('#update-message').focus();
    $('.acc_selector').each(function() {
        if (account_id != '') {
            $(this).attr('disabled', 'disabled');
        } else {
            $(this).removeAttr('disabled');
        }
        $(this).attr('checked', false);
    });
    $('#acc-selector-' + account_id).attr('checked', true);
}

function close_update_box(keep_modal, fade) {
    var status = $('#update-box').attr('name');
    if (status != '') return;
    hide_notice();


    if ((fade == undefined) || (fade == true)) {
        $('#update-box').fadeOut(400, reset_update_box)
    } else {
        $('#update-box').hide()
        reset_update_box()
    }
    if ((keep_modal == undefined) || (keep_modal == false))
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

function done_update_box_with_direct() {
    $('#update-box').attr('name', '');
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
    var in_reply = $('#in-reply-to-id').val();
    if (in_reply == '') {
        $('.acc_selector').each(function() {
            $(this).removeAttr('disabled');
        });
    }
    $('#update-box').attr('name', '');
    $('#progress-box-updatebox').hide();
    $('#progress-msg-updatebox').html('');
    $('#buttonbox-update').show();
}

function count_chars() {
    var count = MAXCHARLIMIT - $('#update-message').val().length;
    $('#char-counter').html(count);
    if (count < 10) {
        $('#char-counter').addClass('maxchar');
    } else {
        $('#char-counter').removeClass('maxchar');
    }
}

/* Statuses */

function lock_status(status_id, message) {
    $('.' + status_id).each(function() {
        var optionsbox = $(this).children('.options');
        // buttonbox
        optionsbox.children(':nth-child(1)').hide();
        // progressbox
        var progressbox = optionsbox.children(':nth-child(2)');
        progressbox.show();
        // progressmsg
        progressbox.children('label:first').html(message);
        // indicator
        $(this).children('input:first').val(message);
    });
}

function unlock_status(status_id) {
    $('.' + status_id).each(function() {
        var optionsbox = $(this).children('.options');
        // buttonbox
        optionsbox.children(':nth-child(1)').show();
        // progressbox
        var progressbox = optionsbox.children(':nth-child(2)');
        progressbox.hide();
        // progressmsg
        progressbox.children('label:first').html('');
        // indicator
        $(this).children('input:first').val('');
    });
}

function update_favorite_mark(status_id, cmd, label, visible) {
    $('.' + status_id).each(function() {
        // favcmd
        var favcmd = $(this).find('a[name="fav-cmd"]:first');
        favcmd.attr('href', cmd);
        favcmd.html(label);

        // favicon
        var favicon = $(this).find('div[name="fav-icon"]');
        if (visible == true)
            favicon.show();
        else
            favicon.hide();
    });
}

function update_retweeted_mark(status_id, cmd, label, visible) {
    $('.' + status_id).each(function() {
        // repeatcmd
        var repeatcmd = $(this).find('a[name="repeat-cmd"]');
        repeatcmd.attr('href', cmd);
        repeatcmd.html(label);

        // repeaticon
        var repeaticon = $(this).find('div[name="repeat-icon"]');
        if (visible == true)
            repeaticon.show();
        else
            repeaticon.hide();
    });
}

function update_profile_follow_cmd(cmd, label) {
    $('#profile-follow-cmd').attr('href', cmd);
    $('#profile-follow-cmd').html(label);
}

function update_profile_mute_cmd(cmd, label) {
    $('#profile-mute-cmd').attr('href', cmd);
    $('#profile-mute-cmd').html(label);
}

function delete_status(status_id) {
    $('.' + status_id).hide('slow', function() {
        $(this).remove();
    });
}

/* Profile Window */

function show_profile_window(account_id, username) {
    console.log('show_profile_window')
    if ($('#profile-window-content').is(':visible')) {
        close_profile_window(true, false)
    }
    $('#modal').fadeIn();
    $('#profile-window').fadeIn();
    $('#progress-box-profile-window').fadeIn();
    exec_command('cmd:show_profile:' + account_id + ARG_SEP + username);
}

function update_profile_window2(profile) {
    $('#progress-box-profile-window').hide()
    $('#profile-window-content').html(profile)
    enable_click_events()
    enable_trigger()
}

function send_direct_from_profile(account_id, username) {
    var message = $('#update-message');
    show_update_box_for_direct(account_id, username);
    close_profile_window(true);
    message.focus();
}

function profile_window_error(message) {
    $('#progress-box-profile-window').hide();
    show_notice(message, 'error');
}

function close_profile_window(keep_modal, fade) {
    if ($('#indicator-profile-window').val() != '')
        return;
    hide_notice();
    if ((fade == undefined) || (fade == true)) {
        console.log('Closing with fade')
        $('#profile-window').fadeOut(400, reset_profile_window)
    } else {
        console.log('Closing without fade')
        $('#profile-window').hide()
        reset_profile_window()
    }
    if ((keep_modal == undefined) || (keep_modal == false))
        $('#modal').fadeOut(400);
}

function reset_profile_window() {
    $('#profile-window-content').html('');
}

function lock_profile(message) {
    $('#profile-options').hide();
    $('#progress-box-profile-options').show();
    $('#progress-msg-profile-options').html(message);
    $('#indicator-profile-window').val(message);
}

function unlock_profile() {
    $('#progress-box-profile-options').hide();
    $('#progress-msg-profile-options').html('');
    $('#indicator-profile-window').val('');
    $('#profile-options').show();
}

/* Autocomplete */

function build_autocomplete_dialog(title, addcmd, index) {
    $('#modal').fadeIn();
    $('#modal').css('z-index', 101);
    if (index != undefined)
        $('#autocomplete-index').val(index);
    $('#autocomplete-window-title').html(title);
    $('#autocomplete-add-cmd').attr('href', 'javascript: ' + addcmd);
    $('#autocomplete-add-function').val(addcmd);
    $('#autocomplete-window').fadeIn();
    $('#autocomplete-username').focus();
}

function show_autocomplete_for_status(index) {
    build_autocomplete_dialog('<% $add_friend %>', 'select_friend();', index);
}

function show_autocomplete_for_direct() {
    build_autocomplete_dialog('<% $select_user %>', 'select_friend_for_direct();');
}

function show_autocomplete_for_profile(account_id) {
    build_autocomplete_dialog('<% $select_user %>', 'select_friend_for_profile("' + account_id + '");');
}

function close_autocomplete_window(keep_modal, fade) {
    var status = $('#autocomplete-window').attr('name');
    if (status != '') return;

    if ((fade == undefined) || (fade == true)) {
        $('#autocomplete-window').fadeOut(400, reset_autocomplete_window)
    } else {
        $('#autocomplete-window').hide()
        reset_autocomplete_window()
    }

    console.log($('#update-box').is(":visible") + ' ' + keep_modal)
    if (!$('#update-box').is(":visible"))
        $('#modal').fadeOut(400)
    else if ((keep_modal == undefined) || (keep_modal == false))
        $('#modal').fadeOut(400);

}

function reset_autocomplete_window() {
    $('#autocomplete-index').val('');
    $('#autocomplete-username').val('');
    $('#modal').css('z-index', 99);
    if ($('#update-box').is(":visible")) {
        $('#update-message').focus();
    }
}

function lock_autocomplete() {
    $('#autocomplete-username').attr('disabled', 'disabled');
    $('#autocomplete-load-cmd').css('opacity', 0.4);
    $('#autocomplete-load-cmd').attr('href', '#');
    $('#buttonbox-autocomplete').hide();
    $('#progress-box-autocomplete').show();
}

function unlock_autocomplete() {
    username = $('#autocomplete-username');
    username.removeAttr('disabled');
    load_cmd = $('#autocomplete-load-cmd');
    load_cmd.attr('href', "javascript: load_friends();");
    load_cmd.css('opacity', 1);
    $('#buttonbox-autocomplete').show();
    $('#progress-box-autocomplete').hide();
    username.focus();
}

function load_friends() {
    lock_autocomplete()
    exec_command('cmd:load_friends')
}

function update_friends(array, skip_unlock) {
    FRIENDS = array;
    var label = '';
    var plabel = "<% $friends %>";
    var slabel = "<% $friend %>";

    if (FRIENDS.length == 1)
        label = FRIENDS.length + ' ' + slabel;
    else
        label = FRIENDS.length + ' ' + plabel;

    $('#friends_counter').html(label);
    $('#autocomplete-username').autocompleteArray(FRIENDS, {delay:10, minChars:1,
        matchSubset:1, maxItemsToShow:10, onItemSelect: autocomplete_friend});
    if ((skip_unlock == undefined) || (skip_unlock == false)) {
        unlock_autocomplete();
    }
}

function select_friend(value) {
    var username = null;
    if (value == undefined) {
        username = $('#autocomplete-username').val();
    } else {
        username = value;
    }
    var message = $('#update-message');
    var index = parseInt($('#autocomplete-index').val());
    var text = message.val();
    var prevtext = text.substring(0, index + 1);
    var nexttext = text.substring(index + 1, text.length);

    if (nexttext.charAt(0) != ' ')
        username += ' '

    var newtext = prevtext + username + nexttext;
    message.val(newtext);
    close_autocomplete_window(true);
    count_chars();
    message.focus();
    message.setCursorPosition(index + username.length + 1);
}

function select_friend_for_direct() {
    close_autocomplete_window(true)
    show_update_box_for_direct('', $('#autocomplete-username').val())
}

function select_friend_for_profile(account_id) {
    close_autocomplete_window(true)
    console.log(account_id)
    show_profile_window(account_id, $('#autocomplete-username').val())
}

function autocomplete_friend(value) {
    eval($('#autocomplete-add-function').val())
}

/* Confirm window */

function show_confirm_window(title, message, cmd) {
    close_update_box(true, false)
    close_autocomplete_window(true, false)
    close_profile_window(true, false)

    console.log('confirm action: ' + title + ' ' + message + ' ' + cmd);
    $('#modal').fadeIn();
    $('#confirm-window').fadeIn();

    $('#confirm-window-cmd').val(cmd)
    $('#confirm-window-title').html(title)
    $('#confirm-window-message').html(message)
}

function reset_confirm_window() {
}

function execute_confirm_window() {
    var cmd = $('#confirm-window-cmd').val()
    console.log('Confirmed command: ' + cmd)
    close_confirm_window()
    exec_command(cmd)
}

function close_confirm_window(keep_modal, fade) {
    if ((fade == undefined) || (fade == true)) {
        console.log('Closing with fade')
        $('#confirm-window').fadeOut(400, reset_confirm_window)
    } else {
        console.log('Closing without fade')
        $('#confirm-window').hide()
        reset_confirm_window()
    }
    if ((keep_modal == undefined) || (keep_modal == false))
        $('#modal').fadeOut(400);
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

function show_replies_to_status(status_id, animated) {
    recalculate_column_size();
    enable_trigger();
    if (animated == true)
        $('#replycontainer-' + status_id).fadeIn(1000);
    else
        $('#replycontainer-' + status_id).show();
    $('#bubble-' + status_id).show();
}

function hide_replies_to_status(status_id) {
    $('#bubble-' + status_id).hide();
    $('#replycontainer-' + status_id).fadeOut(1000);
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

function mute_user(username, mute) {
    $('.tweet .content .name').each(function(){
        var html = $(this).html();
        var start = html.indexOf('>') + 1;
        var end = html.length - 4;
        var name = html.substring(start, end);
        if (name == username) {
            if (mute == true) {
                $(this).parent().parent().parent().hide();
            } else {
                $(this).parent().parent().parent().show();
            }
        }
    });
}

function set_update_box_message(message) {
    console.log('update-message: ' + message);
    $('#update-message').val(message);
    count_chars();
    unlock_update_box();
}

/* Commands */

function update_status() {
    var selected = '';
    var in_reply_to_id = $('#in-reply-to-id').val();
    var direct_message_to = $('#direct-message-to').val();
    var text = $('#update-message').val();
    var accounts = 0;
    $('.acc_selector').each(function() {
        if ($(this).attr('checked')) {
            if (selected == '')
                selected = $(this).val();
            else
                selected += '|' + $(this).val();
            accounts += 1;
        }
    });

    if (accounts > 0) {
        if (text == '') {
            show_notice('<% $you_must_write_something %>', 'warning');
        } else if (text.length > MAXCHARLIMIT) {
            show_notice('<% $message_like_testament %>', 'warning');
        } else {
            if (direct_message_to != '') {
                /* Direct message */
                if (accounts > 1) {
                    show_notice('<% $can_send_message_to_one_account %>', 'warning');
                } else {
                    lock_update_box('<% $sending_message %>');
                    exec_command('cmd:direct_message:' + selected + ARG_SEP + direct_message_to + ARG_SEP + packstr(text));
                }
            } else {
                /* Regular status */
                lock_update_box('<% $updating_status %>');
                if (in_reply_to_id == ''){
                    exec_command('cmd:update_status:' + selected + ARG_SEP + packstr(text));
                } else {
                    exec_command('cmd:reply_status:' + selected + ARG_SEP + in_reply_to_id + ARG_SEP + packstr(text));
                }
            }
        }
    } else {
        show_notice('<% $select_account_to_post %>', 'warning');
    }
}

function quote_status(account_id, username, text) {
    // To clean the message
    var message = text.replace('&gt;', '>');
    message = message.replace('&lt;', '<');
    //console.log(account_id + ',' + username + ',' + text);
    var rt = "RT @" + username + ": " + message;
    show_update_box(rt);
}

function reply_status(account_id, status_id, title, mentions) {
    //console.log(account_id + ',' + status_id + ',' + mentions)
    var msg = "";
    for (var i=0; i < mentions.length; i++) {
        if (msg.indexOf(mentions[i]) < 0) {
            msg += "@" + mentions[i] + " "
        }
    }
    show_update_box(msg, status_id, account_id, title)
}

function reply_direct(account_id, username) {
    console.log(account_id + ' ' + username);
    show_update_box_for_direct(account_id, username);
}

function short_url() {
    var text = $('#update-message').val();

    if (text == '') {
        show_notice('<% $you_must_write_something %>', 'warning');
    } else {
        lock_update_box('<% $shorting_urls %>');
        exec_command('cmd:short_urls:' + packstr(text));
    }
}

function show_avatar(account_id, username) {
    exec_command('cmd:profile_image:' + account_id + ARG_SEP + username);
}

function remove_statuses(column_id, number, max_statuses) {
    console.log(column_id + ' ' + number + ' ' + max_statuses);
    var max = parseInt(number);
    var count = 1;
    var statuses = $('#list-' + column_id + " .tweet").get();
    console.log(statuses.length + ' statuses in column ' + column_id);
    // Don't remove if there is left space for more tweets
    if ((statuses.length + number) <= max_statuses)
        return;

    for (var i = 1; i <= max; i++) {
        var tweet = $('#list-' + column_id + ' .tweet:last-child');
        var t_id = tweet.attr('class');
        tweet.remove();
        console.log('Removing status: #list-' + column_id + ' ' + t_id + ' (' + i + ' de ' + max + ')');
    }
}

function remove_duplicates(column_id, status_ids) {
    for (var i = 0; i < status_ids.length; i++) {
        if ($('#list-' + column_id + " .tweet." + status_ids[i]).length > 0) {
            console.log('Removing duplicated status: #list-' + column_id + " .tweet." + status_ids[i]);
            $('#list-' + column_id + " .tweet." + status_ids[i]).remove();
        }
    }
}

function show_about() {
    exec_command('cmd:about:');
}

function show_accounts() {
    exec_command('cmd:accounts_manager:');
}


function show_preferences() {
    exec_command('cmd:preferences:');
}

jQuery(document).bind('keydown', 'Ctrl+n',function (evt){show_update_box(); return false; });
jQuery(document).bind('keydown', 'Ctrl+d',function (evt){show_autocomplete_for_direct(); return false; });
jQuery(document).bind('keydown', 'Ctrl+b',function (evt){show_about(); return false; });
jQuery(document).bind('keydown', 'Ctrl+a',function (evt){show_accounts(); return false; });
jQuery(document).bind('keydown', 'Ctrl+p',function (evt){show_preferences(); return false; });
