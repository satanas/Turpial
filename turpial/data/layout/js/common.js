var timeout = null;
var reset = null;

function exec_command(cmd) {
    document.getElementById("query").src = cmd;
    window.location = cmd;
}

function show_notice(message, type) {
    $('#alert-label').html(message);
    $('#alert-message').fadeIn();
    $('#alert-message').addClass(type);
    timeout = setTimeout(function(){hide_notice()}, 5000);
}

function hide_notice(force) {
    clearTimeout(timeout);
    if (force == undefined)
        $('#alert-message').fadeOut();
    else if (force == true)
        $('#alert-message').hide();
    reset = setTimeout(function(){reset_notice()}, 500);
}

function reset_notice() {
    clearTimeout(reset);
    $('#alert-label').html('');
    $('#alert-message').removeClass('error');
    $('#alert-message').removeClass('warning');
    $('#alert-message').removeClass('info');
}
