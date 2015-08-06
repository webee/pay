$(document).ready(function () {
    $('.hqyzm').click(function () {
        $.ajax('/withdraw/generate-identifying-code', {
            type: 'post',
            success: function (data, textStatus) {
                var message = textStatus === 'success'
                    ? '验证码已发送至注册领队时所留手机号'
                    : '验证码发送失败，请重试。';
                $('.identifying-code.warn').html(message);
            }
        });
    });
});