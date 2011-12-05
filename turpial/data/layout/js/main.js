var num_columns = 1;
var dock_visible = true;

$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
    
    activate_options_trigger();
});

function recalculate_column_size(nw, nh) {
    var width = window.innerWidth;
    var height = window.innerHeight;
    if (nw != undefined)
        width = nw;
    if (nh != undefined)
        height = nh;
    
    var content_height = height - 23;
    var notice_width = width - 120;
    var column_width = (width / num_columns) - 1;
    var column_height = content_height; /*height;*/
    var wrapper_height = height - 32;
    var empty_wrapper_height = column_height;
    var empty_list_height = height - 15;
    var list_width = column_width - 11;
    var list_height = column_height - 45;
    var empty_logo_top = empty_list_height / 5;
    var combo_width = column_width - 83;
    var tweet_width = column_width - 120;
    
    $('#content').css('height', content_height + 'px');
    $('.column').css('width', column_width + 'px');
    $('.column').css('height', column_height + 'px');
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
