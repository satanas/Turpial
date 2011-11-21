var num_columns = 1;
var dock_visible = true;

$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
    
    $('.content').mouseenter(function() {
        console.log('content mouseenter');
        var name = $(this).attr('name');
        $('#options-' + name).show();
    });
    
    $('.content').mouseleave(function() {
        console.log('content mouseleave');
        var name = $(this).attr('name');
        $('#options-' + name).hide();
    });
    
    $('#hider').click(function(){
        if (dock_visible == true) {
            $('#dock').slideUp();
            $('#hider').css('background', '#3c3b37 url(\'../../pixmaps/hider-up-background.png\') no-repeat');
            dock_visible = false;
        } else {
            $('#dock').slideDown();
            $('#hider').css('background', '#3c3b37 url(\'../../pixmaps/hider-down-background.png\') no-repeat');
            dock_visible = true;
        }
    });
});

function recalculate_column_size(nw, nh) {
    var width = window.innerWidth;
    var height = window.innerHeight;
    if (nw != undefined)
        width = nw;
    if (nh != undefined)
        height = nh;
    
    var dock_left = (width - 260) / 2;
    var column_width = (width / num_columns) - 1;
    var column_height = height;
    var wrapper_height = height - 32;
    var empty_wrapper_height = column_height;
    var empty_list_height = height - 15;
    var list_width = column_width - 11;
    var list_height = column_height - 45;
    var empty_logo_top = empty_list_height / 5;
    var combo_width = column_width - 83;
    var tweet_width = column_width - 120;
    
    $('#dock-container').css('left', dock_left + 'px');
    $('.column').css('width', column_width + 'px');
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

function show_status_options(id) {
    $('#options-' + id).slideDown();
}
