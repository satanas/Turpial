$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
});

function recalculate_column_size() {
    var column_width = window.innerWidth - 2;
    var new_list_width = window.innerWidth - 25;
    var new_list_height = window.innerHeight - 60;
    $('#list').css('width', new_list_width + 'px');
    $('#list').css('height', new_list_height + 'px');
}
