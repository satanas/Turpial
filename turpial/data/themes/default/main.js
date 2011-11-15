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
    
    /*$('.options').mouseleave(function() {
        $(this).hide();
    });
    
    $('.tweet .content .info').mouseenter(function() {
        var name = $(this).attr('name');
        $('#options-' + name).show();
    });*/
    
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
    
    var new_dock_left = ((window.innerWidth - 315) / 2) + 20;
    var new_wrapper_height = window.innerHeight - 32;
    var new_col_height = new_wrapper_height - 15;
    var empty_col_height = window.innerHeight - 15;
    
    $('.wrapper').css('height', new_wrapper_height + 'px');
    $('.empty-wrapper').css('height', window.innerHeight + 'px');
    $('.empty-list').css('height', empty_col_height + 'px');
    $('.list').css('height', new_col_height + 'px');
    
    var new_width = $('#wrapper1').width() - 13;
    var combo_width = $('#wrapper1').width() - 83;
    var tweet_width = new_width - 105;
    
    $('.list').css('width', new_width + 'px');
    $('.empty-list').css('width', new_width + 'px');
    $('.combo').css('width', combo_width + 'px');
    $('.tweet .content').css('width', tweet_width + 'px');
    $('#dock-container').css('left', new_dock_left + 'px');
}

function show_status_options(id) {
    $('#options-' + id).slideDown();
}
