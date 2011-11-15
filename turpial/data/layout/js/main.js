var num_columns = 1;
var dock_visible = true;

$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
    
    $('.content').mouseenter(function() {
        var name = $(this).attr('name');
        $('#options-' + name).show();
    });
    
    $('.content').mouseleave(function() {
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

function recalculate_column_size() {
    var dock_left = (window.innerWidth - 260) / 2;
    var column_width = (window.innerWidth - 2) / num_columns;
    var column_height = window.innerHeight;
    var wrapper_height = window.innerHeight - 32;
    var empty_wrapper_height = column_height;
    var empty_list_height = window.innerHeight - 15;
    var list_width = column_width - 11;
    var list_height = column_height - 11;
    var empty_logo_top = empty_list_height / 5;
    
    $('#dock-container').css('left', dock_left + 'px');
    $('.column').css('width', column_width + 'px');
    $('.wrapper').css('height', wrapper_height + 'px');
    $('.wrapper').css('width', column_width + 'px');
    $('.empty-wrapper').css('height', wrapper_height + 'px');
    $('.empty-wrapper').css('width', column_width + 'px');
    
    $('.list').css('width', list_width + 'px');
    $('.empty-list').css('width', list_width + 'px');
    $('.empty-list').css('height', empty_list_height + 'px');
    $('.empty-logo').css('margin-top', empty_logo_top + 'px');
    
    /*$('.list').css('height', col_height + 'px');
    
    
    
    var new_width = $('#wrapper1').width() - 13;
    var combo_width = $('#wrapper1').width() - 83;
    var tweet_width = new_width - 105;
    
    $('.empty-list').css('width', new_width + 'px');
    
    $('.combo').css('width', combo_width + 'px');
    $('.tweet .content').css('width', tweet_width + 'px');*/
}

function show_status_options(id) {
    $('#options-' + id).slideDown();
}

function draw_columns(columns) {
    alert(columns);
}
