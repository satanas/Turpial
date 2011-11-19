$(document).ready(function() {
    enable_mouseover();
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
});

function after_update() {
    enable_mouseover();
}

function enable_mouseover() {
    $('.account').mouseenter(function() {
        var name = $(this).attr('id');
        $('#options-' + name).show();
    });
    
    $('.account').mouseleave(function() {
        var name = $(this).attr('id');
        $('#options-' + name).hide();
    });
}

function recalculate_column_size() {
    var column_width = window.innerWidth - 2;
    var new_list_width = window.innerWidth - 25;
    var new_list_height = window.innerHeight - 60;
    $('#list').css('width', new_list_width + 'px');
    $('#list').css('height', new_list_height + 'px');
}

function delete_account(acc) {
    var rtn = confirm('<% $delete_account_confirm %> ' + acc);
    if (rtn == true)
        exec_command('cmd:delete_account:' + acc);
}
