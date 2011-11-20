var timeout = null;
var reset = null;

function configure_notice(top, left) {
    $('#notice').css('top', top);
    $('#notice').css('left', left);
}

function show_notice(message, type) {
    $('#notice').html(message);
    $('#notice').addClass(type);
    $('#notice').fadeIn();
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
    $('#notice').removeClass('info');
}

function exec_command(cmd) {
    $("#query").attr('src') = cmd;
    $(window).location = cmd;
}
