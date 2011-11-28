var all_columns = new Object;
var all_accounts = new Object;

$(document).ready(function() {
    recalculate_column_size();
    $(window).resize(function() {
        recalculate_column_size();
    });
    activate_change_trigger();
});

function recalculate_column_size() {
    var column_width = window.innerWidth - 2;
    var new_list_width = window.innerWidth - 25;
    var new_list_height = window.innerHeight - 60;
    $('#list').css('width', new_list_width + 'px');
    $('#list').css('height', new_list_height + 'px');
}

function activate_change_trigger() {
    $('.account').change(function() {
        var start = $(this).attr('id').indexOf('_');
        var length = $(this).attr('id').length;
        var col_id = $(this).attr('id').substr(start + 1, length);
        /*var col_id = $(this).attr('name');*/
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
    $('#stream_' + col_id).html(options);
}

function new_column() {
    var count = $('.column').length;
    exec_command('cmd:new_column:' + count);
}

function delete_column(col_id) {
    var count = 0;
    $('#column_' + col_id).remove();
    $('.column').each(function() {
        count++;
        var curr_id = $(this).attr('name');
        $('#column_' + curr_id).attr('name', count);
        $('#column_' + curr_id).attr('id', 'column_' + count);
        $('#label_' + curr_id).attr('id', 'label_' + count);
        $('#account_' + curr_id).attr('id', 'account_' + count);
        $('#stream_' + curr_id).attr('id', 'stream_' + count);
        $('#action_' + curr_id).attr('href', "javascript: delete_column('" + count + "');");
        $('#action_' + curr_id).attr('id', 'action_' + count);
        $('#label_' + count).html(count);
    });
}

function save_columns() {
    var cmd = 'cmd:save_columns:';
    $('.column').each(function() {
        var curr_id = $(this).attr('name');
        var acc_id = $('#account_' + curr_id).val();
        var col_id = $('#stream_' + curr_id).val();
        cmd += curr_id + '|' + acc_id + '|' + col_id + '^';
    });
    
    cmd = cmd.substr(0, cmd.length - 1);
    exec_command(cmd);
}
