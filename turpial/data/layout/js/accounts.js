$(document).ready(function() {
    enable_mouseover();
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

function delete_account(acc) {
    var rtn = confirm('<% $delete_account_confirm %> ' + acc);
    if (rtn == true)
        exec_command('cmd:delete_account:' + acc);
}
