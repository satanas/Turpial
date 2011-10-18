$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
});

function recalculate_column_size() {
    
    var new_wrapper_height = window.innerHeight - 32;
    var new_col_height = new_wrapper_height - 15;
    
    $('.wrapper').css('height', new_wrapper_height + 'px');
    $('.list').css('height', new_col_height + 'px');
    
    var new_width = $('#wrapper1').width() - 13;
    var combo_width = $('#wrapper1').width() - 83;
    var tweet_width = new_width - 105;
    
    $('.list').css('width', new_width + 'px');
    $('.combo').css('width', combo_width + 'px');
    $('.tweet .content').css('width', tweet_width + 'px');
}
