$(document).ready(function () {
    var wait = 60;

    function timing(btn) {
        if (wait == 0) {
            btn.removeAttribute("disabled");
            btn.value = "获取验证码";
            wait = 60;
        } else {
            btn.setAttribute("disabled", true);
            btn.value = "重新发送(" + wait + ")";
            wait--;
            setTimeout(function () {
                timing(btn)
            }, 1000);
        }
    }

    $('.hqyzm').click(function () {
        $('.identifying-code.warn').html('正在获取中......');
        timing(this);
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