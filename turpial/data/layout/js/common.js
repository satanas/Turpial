var timeout = null;
var reset = null;

function exec_command(cmd) {
    document.getElementById("query").src = cmd;
    window.location = cmd;
}

function show_notice(message, type) {
    $('#notice').html(message);
    $('#notice').fadeIn();
    $('#notice').addClass(type);
    timeout = setTimeout(hide_notice, 5000);
}

function hide_notice(force) {
    clearTimeout(timeout);
    if (force == undefined)
        $('#notice').fadeOut();
    else if (force == true)
        $('#notice').hide();
    reset = setTimeout(reset_notice, 500);
}

function reset_notice() {
    clearTimeout(reset);
    $('#notice').html('');
    $('#notice').removeClass('error');
    $('#notice').removeClass('warning');
    $('#notice').removeClass('info');
}
