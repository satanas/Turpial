var timeout = null;
var reset = null;

function exec_command(cmd) {
    document.getElementById("query").src = cmd;
    window.location = cmd;
}

function show_notice(container, message, type) {
    var cid = '#' + container + '-notice';
    $(cid).html(message);
    $(cid).fadeIn();
    $(cid).addClass(type);
    timeout = setTimeout(function(){hide_notice(cid)}, 5000);
}

function hide_notice(cid, force) {
    clearTimeout(timeout);
    if (force == undefined)
        $(cid).fadeOut();
    else if (force == true)
        $(cid).hide();
    reset = setTimeout(function(){reset_notice(cid)}, 500);
}

function reset_notice(cid) {
    clearTimeout(reset);
    $(cid).html('');
    $(cid).removeClass('error');
    $(cid).removeClass('warning');
    $(cid).removeClass('info');
}
