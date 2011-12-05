var num_columns = 1;
var dock_visible = true;
var timeout = null;
var reset = null;

$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
    
    activate_options_trigger();
    show_notice('La puta que te pario con este mensaje tan jodidamente largo', 'error');
});

function recalculate_column_size(nw, nh) {
    var width = window.innerWidth;
    var height = window.innerHeight;
    if (nw != undefined)
        width = nw;
    if (nh != undefined)
        height = nh;
    
    var content_height = height - 23;
    var notice_container_width = width - 120;
    var notice_width = notice_container_width - 20;
    var column_width = (width / num_columns) - 1;
    var column_height = content_height;
    var wrapper_height = height - 32;
    var empty_wrapper_height = column_height;
    var empty_list_height = height - 15;
    var list_width = column_width - 11;
    var list_height = column_height - 45;
    var empty_logo_top = empty_list_height / 5;
    var combo_width = column_width - 83;
    var tweet_width = column_width - 100;
    
    $('#content').css('height', content_height + 'px');
    $('.column').css('width', column_width + 'px');
    $('.column').css('height', column_height + 'px');
    $('#notice-container').css('width', notice_container_width + 'px');
    $('#notice').css('width', notice_width + 'px');
    $('.wrapper').css('height', wrapper_height + 'px');
    $('.wrapper').css('width', column_width + 'px');
    $('.empty-wrapper').css('height', wrapper_height + 'px');
    $('.empty-wrapper').css('width', column_width + 'px');
    
    $('.list').css('height', list_height + 'px');
    $('.list').css('width', list_width + 'px');
    $('.empty-list').css('width', list_width + 'px');
    $('.empty-list').css('height', empty_list_height + 'px');
    $('.empty-logo').css('margin-top', empty_logo_top + 'px');
    
    $('.combo').css('width', combo_width + 'px');
    $('.tweet .content').css('width', tweet_width + 'px');
}

function activate_options_trigger() {
    $('.content').mouseenter(function() {
        var name = $(this).attr('name');
        console.log(name);
        $('#options-' + name).show();
    });
    
    $('.content').mouseleave(function() {
        var name = $(this).attr('name');
        console.log(name);
        $('#options-' + name).hide();
    });
}

function show_status_options(id) {
    $('#options-' + id).slideDown();
}

function show_notice(message, type) {
    $('#notice').html(message);
    $('#notice').fadeIn();
    $('#notice').addClass(type);
    timeout = setTimeout(hide_notice, 5000);
}

function hide_notice(force) {
    clearTimeout(timeout);
    if (force == undefined)
        $('#notice').fadeOut();
    else if (force == true)
        $('#notice').hide();
    reset = setTimeout(reset_notice, 500);
}

function reset_notice() {
    clearTimeout(reset);
    $('#notice').html('');
    $('#notice').removeClass('error');
    $('#notice').removeClass('warning');
    $('#notice').removeClass('info');
}
