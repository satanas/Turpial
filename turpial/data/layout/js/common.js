var timeout = null;
var reset = null;

function exec_command(cmd) {
    if (typeof fireToPython != 'undefined') {
        if(typeof fireToPython.send == 'function') {
            fireToPython.send(cmd)
        }
    } else {
        window.location = cmd;
    }
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

function packstr(str) {
    return window.btoa(unescape(encodeURIComponent(str)));
}

new function($) {
    $.fn.getCursorPosition = function() {
        var pos = 0;
        var el = $(this).get(0);
        // IE Support
        if (document.selection) {
            el.focus();
            var Sel = document.selection.createRange();
            var SelLength = document.selection.createRange().text.length;
            Sel.moveStart('character', -el.value.length);
            pos = Sel.text.length - SelLength;
        }
        // Firefox support
        else if (el.selectionStart || el.selectionStart == '0')
            pos = el.selectionStart;

        return pos;
    }
} (jQuery);

new function($) {
    $.fn.setCursorPosition = function(pos) {
        var el = $(this).get(0);
        if (el.setSelectionRange) {
            el.setSelectionRange(pos, pos);
        } else if (el.createTextRange) {
            var range = el.createTextRange();
            range.collapse(true);
            range.moveEnd('character', pos);
            range.moveStart('character', pos);
            range.select();
        }
    }
}(jQuery);
