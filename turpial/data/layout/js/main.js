var maxcharlimit = 140;
var dock_elements = 6;
var num_columns = <% @num_columns %>;

$(document).ready(function() {
    recalculate_column_size();
    $('#alert-message').click(function() {
        hide_notice();
    });
    $(window).resize(function() {
        recalculate_column_size();
    });
    count_chars();
    enable_updatebox_toggle();
    show_notice('Retweeted successfully', 'info');
});

function recalculate_column_size(nw, nh) {
    var width = window.innerWidth;
    var height = window.innerHeight;
    if (nw != undefined)
        width = nw;
    if (nh != undefined)
        height = nh;
    
    var content_height = height - 23;
    var dock_width = 22 * dock_elements;
    var main_notice_container_width = width - (22 * dock_elements) - 10;
    var main_notice_width = main_notice_container_width - 20;
    var updatebox_notice_width = width - 170;
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
    
    $('#content').css('height', content_height + 'px');
    $('.column').css('width', column_width + 'px');
    $('.column').css('height', column_height + 'px');
    $('#dock').css('width', dock_width + 'px');
    $('#main-notice-container').css('width', main_notice_container_width + 'px');
    $('#main-notice').css('width', main_notice_width + 'px');
    $('#updatebox-notice').css('width', updatebox_notice_width + 'px');
    $('.wrapper').css('height', wrapper_height + 'px');
    $('.wrapper').css('width', column_width + 'px');
    
    $('.list').css('height', list_height + 'px');
    $('.list').css('width', list_width + 'px');
    $('.combo').css('width', combo_width + 'px');
    $('.tweet .content').css('width', tweet_width + 'px');
    
    //$('#update-message').css('width', update_msg_width + 'px');
    $('.message-container').css('width', update_msg_width + 'px');
    
    $('#alert-message').css('width', alert_msg_width + 'px');
    $('#alert-message').css('left', alert_msg_left + 'px');
    $('#alert-label').css('width', alert_lbl_width + 'px');
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

function enable_updatebox_toggle() {
    $('.toggle').click(function() {
        $(this).toggleClass('down');
    });
}

function show_update_box() {
    $('#modal').fadeIn();
    $('#update-box').fadeIn();
    $('#update-message').focus();
}

function close_update_box() {
    var status = $('#update-box').attr('name');
    if (status != '') return;
    unlock_updatebox();
    hide_notice();
    $('#update-box').fadeOut(400, reset_update_box);
    $('#modal').fadeOut(400);
}

function count_chars() {
    $('#update-message').keyup(function(event) {
        console.log('tecla: ' + event.keyCode);
        if (event.keyCode == 27) {
            close_update_box();
            return;
        }
        var count = maxcharlimit - $('#update-message').val().length;
        $('#char-counter').html(count);
        if (count < 10) {
            $('#char-counter').addClass('maxchar');
        } else {
            $('#char-counter').removeClass('maxchar');
        }
    });
}

function reset_update_box() {
    $('#update-message').val('');
    $('#char-counter').html('140');
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

function update_status() {
    var selected = false;
    var text = $('#update-message').val();
    $('.acc_selector').each(function() {
        if ($(this).attr('checked'))
            selected = true;
    });
    if (selected) {
        if (text == '') {
            show_notice('<% $you_must_write_something %>', 'warning');
        } else if (text.length > maxcharlimit) {
            show_notice('<% $message_like_testament %>', 'warning');
        } else {
            lock_updatebox('Sending...');
            alert(text);
        }
    } else {
        show_notice('<% $select_account_to_post %>', 'warning');
    }
}

function lock_updatebox(message) {
    $('#update-box').attr('name', message);
    $('#update-message').attr('disabled', 'disabled');
    $('.acc_selector').each(function() {
        $(this).attr('disabled', 'disabled');
    });
    $('#buttonbox-update').hide();
    $('#progress-box-updatebox').show();
    $('#progress-msg-updatebox').html(message);
}

function unlock_updatebox() {
    $('#update-box').attr('name', '');
    $('#update-message').removeAttr('disabled');
    $('.acc_selector').each(function() {
        $(this).removeAttr('disabled');
    });
    $('#progress-box-updatebox').hide();
    $('#progress-msg-updatebox').html('');
    $('#buttonbox-update').show();
}
