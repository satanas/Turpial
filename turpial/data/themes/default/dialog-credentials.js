$(document).ready(function() {
    var ok_btn = $('#ok');
    ok_btn.attr('disabled', 'disabled');
    
    $('#password').keyup(function() {
        var passwd = $('#password').val();
        
        if (passwd.length > 0) {
            ok_btn.removeAttr('disabled');
         } else {
            ok_btn.attr('disabled', 'disabled');
        }
    });
});

function ok() {
    var passwd = $('#password').val();
    var remember = $('#remember').is(':checked');
    window.location = 'cmd:ok:' + passwd + '-%&%-' + remember;
}

function cancel() {
    window.location = 'cmd:cancel';
}
