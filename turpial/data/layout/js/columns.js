var all_columns = new Object;
var all_accounts = new Object;

$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
    activate_change_trigger();
});

function activate_change_trigger() {
    $('.accounts').change(function() {
        var col_id = $(this).attr('name');
        var acc_id = $(this).val();
        update_columns(acc_id, col_id);
    });
}

function update_columns(acc_id, col_id) {
    var options = '<option selected="selected">-- Column --</option>\n'
    if (all_columns[acc_id] != undefined) {
        all_columns[acc_id].forEach(function(item) {
            options += '<option>' + item + '</option>\n';
        });
    }
    $('#column_' + col_id).html(options);
}

function recalculate_column_size() {
    var column_width = window.innerWidth - 2;
    var new_list_width = window.innerWidth - 25;
    var new_list_height = window.innerHeight - 60;
    $('#list').css('width', new_list_width + 'px');
    $('#list').css('height', new_list_height + 'px');
}

function new_column() {
    $('#list').append('Nueva columna');
}

function delete_column(col) {
    alert(all_columns['pupu']);
    var rtn = confirm('<% $delete_column_confirm %> ' + col);
    if (rtn == true)
        exec_command('cmd:delete_column:' + col);
}
