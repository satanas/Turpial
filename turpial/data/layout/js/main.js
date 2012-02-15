var arg_sep = '<% @arg_sep %>';
var maxcharlimit = 140;
var num_columns = <% @num_columns %>;
var friends = [];

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
    $('#imageview').click(function() {
        hide_imageview();
    });
});

function recalculate_column_size(nw, nh) {
    var width = window.innerWidth; // $(window).width();
    var height = window.innerHeight; // $(window).height();
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
    var autocomplete_win_left = (width - 200) / 2;
    
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
    $('#autocomplete-window').css('left', autocomplete_win_left + 'px');
    
    resize_imageview();
}

function change_num_columns(num) {
    num_columns = num;
}

function enable_trigger() {
    $('.tweet').mouseover(function() {
        var indicator = $(this).children('input:first').val();
        if (indicator != "") return;
        $(this).children('.options').children(':nth-child(1)').show();
    });
    
    $('.tweet').mouseleave(function() {
        $(this).children('.options').children(':nth-child(1)').hide();
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
        } else if (e.keyCode == 13) {
            eval($('#autocomplete-add-function').val());
        }
    });
}

function resize_imageview(orig_w, orig_h) {
    var img_w = 0;
    var img_h = 0;
    var width = window.innerWidth;
    var height = window.innerHeight;
    var imageview_border = 100;
    var imageview = $('#imageview');
    
    if (orig_w == undefined)
        orig_w = imageview.width();
    if (orig_h == undefined)
        orig_h = imageview.height();
    
    if (imageview.attr('src') == '') {
        img_h = 200;
        img_w = 200;
    } else {
        var rate = orig_w / orig_h;
        if (rate >= 1) {
            var temp_w = width - imageview_border;
            if (temp_w > orig_w)
                img_w = orig_w;
            else
                img_w = temp_w;
            img_h = img_w / rate;
        } else {
            var temp_h = height - imageview_border;
            if (temp_h > orig_h)
                img_h = orig_h;
            else
                img_h = temp_h;
            img_w = img_h * rate;
        }
    }
    
    imageview.css({
        height: img_h, 
        width: img_w
    });
    $('#imageview-frame').css({ 
        top: (height / 2) - (img_h / 2),
        left: (width / 2) - (img_w / 2)
    });
}

/* Columns */

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
    var count = maxcharlimit - $('#update-message').val().length;
    $('#char-counter').html(count);
    if (count < 10) {
        $('#char-counter').addClass('maxchar');
    } else {
        $('#char-counter').removeClass('maxchar');
    }
}

/* Statuses */

function lock_status(status_id, message) {
    $('div[name="' + status_id + '"]').each(function() {
        // buttonbox
        $(this).children(":nth-child(6)").children(':nth-child(1)').hide();
        // progressbox
        var progressbox = $(this).children(":nth-child(6)").children(':nth-child(2)');
        progressbox.show();
        // indicator
        $(this).children('input:first').val(message);
        // progressmsg
        progressbox.children('label:first').html(message);
    });
}

function unlock_status(status_id) {
    $('div[name="' + status_id + '"]').each(function() {
        // progressbox
        var progressbox = $(this).children(":nth-child(6)").children(':nth-child(2)');
        progressbox.fadeOut(400, function() {
            $(this).children('label:first').html('');
        });
        // indicator
        $(this).children('input:first').val('');
    });
}

function update_favorite_mark(status_id, cmd, label, visible) {
    $('div[name="' + status_id + '"]').each(function() {
        // favcmd
        var favcmd = $(this).find('a[name="fav-cmd"]');
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
    $('div[name="' + status_id + '"]').each(function() {
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
    $('#modal').fadeIn();
    $('#profile-window').fadeIn();
    $('#progress-box-profile-window').fadeIn();
    exec_command('cmd:show_profile:' + account_id + arg_sep + username);
}

function update_profile_window(profile) {
    $('#progress-box-profile-window').hide();
    $('#profile-window-content').html(profile).slideDown();
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

function close_profile_window(keep_modal) {
    var status = $('#profile-window').attr('name');
    if (status != '') return;
    hide_notice();
    $('#profile-window').fadeOut(400, reset_profile_window);
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

function close_autocomplete_window() {
    var status = $('#autocomplete-window').attr('name');
    if (status != '') return;
    $('#autocomplete-window').fadeOut(400, reset_autocomplete_window);
    if (!$('#update-box').is(":visible")) {
        $('#modal').fadeOut(400);
    }
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
    $('#autocomplete-username').removeAttr('disabled');
    $('#autocomplete-load-cmd').attr('href', "javascript: load_friends();");
    $('#autocomplete-load-cmd').css('opacity', 1);
    $('#buttonbox-autocomplete').show();
    $('#progress-box-autocomplete').hide();
}

function load_friends() {
    lock_autocomplete();
    exec_command('cmd:load_friends');
}

function update_friends(array) {
    friends = array;
    var label = '';
    var plabel = "<% $friends %>";
    var slabel = "<% $friend %>";
    
    if (friends.length == 1)
        label = friends.length + ' ' + slabel;
    else
        label = friends.length + ' ' + plabel;
    
    $('#friends_counter').html(label);
    $("#autocomplete-username").autocompleteArray(friends, {delay:10, minChars:1, 
        matchSubset:1, maxItemsToShow:10, onItemSelect: autocomplete_friend});
    unlock_autocomplete();
}

function select_friend(value) {
    var username = null;
    if (username == undefined) {
        username = $('#autocomplete-username').val();
    } else {
        username = value;
    }
    var message = $('#update-message');
    var index = $('#autocomplete-index').val();
    var text = message.val();
    var prevtext = text.substr(0, index + 1);
    var nexttext = text.substr(index + 1, text.length);
    /*
    if (nexttext.substr(0) != ' ')
        username += ' '
    */
    var newtext = prevtext + username + nexttext;
    message.val(newtext);
    close_autocomplete_window();
    message.focus();
    message.setCursorPosition(index + 2 + username.length);
    count_chars();
}

function select_friend_for_direct() {
    close_autocomplete_window();
    show_update_box_for_direct('', $('#autocomplete-username').val());
}

function autocomplete_friend(value) {
    eval($('#autocomplete-add-function').val());
}

/* Images */

function show_imageview(img_url) {
    console.log(img_url);
    $('#modal').fadeIn();
    $('#imageview-window').fadeIn();
    if (img_url == undefined) {
        //Show the loading progress
    } else {
        $('#imageview').attr('src', img_url);
    }
}

function update_imageview(img_url, orig_w, orig_h) {
    $('#progress-box-imageview').hide();
    var imageview = $('#imageview');
    imageview.attr('src', img_url);
    imageview.show();
    resize_imageview(orig_w, orig_h);
}

function hide_imageview() {
    $('#imageview-window').fadeOut(400, function() {
        var imageview = $('#imageview');
        imageview.attr('src', '');
        imageview.css('width', '200px');
        imageview.css('height', '200px');
        imageview.hide();
        resize_imageview();
        $('#progress-box-imageview').show();
        $('#modal').fadeOut(400);
    });
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

function show_replies_to_status(status_id) {
    recalculate_column_size();
    enable_trigger();
    $('#replycontainer-' + status_id).fadeIn(1000);
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
        } else if (text.length > maxcharlimit) {
            show_notice('<% $message_like_testament %>', 'warning');
        } else {
            if (direct_message_to != '') {
                /* Direct message */
                if (accounts > 1) {
                    show_notice('<% $can_send_message_to_one_account %>', 'warning');
                } else {
                    lock_update_box('<% $sending_message %>');
                    exec_command('cmd:direct_message:' + selected + arg_sep + direct_message_to + arg_sep + packstr(text));
                }
            } else {
                /* Regular status */
                lock_update_box('<% $updating_status %>');
                if (in_reply_to_id == ''){
                    exec_command('cmd:update_status:' + selected + arg_sep + packstr(text));
                } else {
                    exec_command('cmd:reply_status:' + selected + arg_sep + in_reply_to_id + arg_sep + packstr(text));
                }
            }
        }
    } else {
        show_notice('<% $select_account_to_post %>', 'warning');
    }
}

function quote_status(account_id, username, text) {
    //console.log(account_id + ',' + username + ',' + text);
    var rt = "RT @" + username + ": " + text;
    show_update_box(rt);
}

function reply_status(account_id, status_id, title, mentions) {
    //console.log(account_id + ',' + status_id + ',' + mentions);
    var msg = "";
    for (var i=0; i < mentions.length; i++) {
        msg += "@" + mentions[i] + " ";
    }
    show_update_box(msg, status_id, account_id, title);
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
    show_imageview();
    exec_command('cmd:profile_image:' + account_id + arg_sep + username);
}
