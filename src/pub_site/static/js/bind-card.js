$(document).ready(function() {
    $('.hqyzm').click(function() {
        $.post('/withdraw/generate-identifying-code', function(data, textStatus) {
            if(textStatus === 'success') {
                $('.identifying-code.warn').html('验证码已发送至注册领队时所留手机号');
            }
        });
    });
});