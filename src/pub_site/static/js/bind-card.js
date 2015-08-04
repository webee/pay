$(document).ready(function() {
    $('.hqyzm').click(function() {
        $.ajax('/withdraw/generate-identifying-code', {
            type: 'post',
            headers: {'X-CSRF-Token': $('#csrf_token').val()},
            success: function(data, textStatus) {
                if(textStatus === 'success') {
                    $('.identifying-code.warn').html('验证码已发送至注册领队时所留手机号');
                }
            }
        });
    });
});