$(document).ready(function () {
    var wait = 60;

    function timing(btn) {
        if (wait == 0) {
            btn.removeAttr("disabled").attr('value', '获取验证码');
            wait = 60;
        } else {
            btn.attr('value','重新发送(' + wait + ')');
            wait--;
            setTimeout(function () {
                timing(btn)
            }, 1000);
        }
    }

    $('.hqyzm').click(function () {
        if (this.getAttribute('data-verified') === "yes") {
            $(this).attr('disabled', 'disabled').attr('value', '正在获取');
            $('.verification-code.warn').html('');
            $.ajax(this.getAttribute('data-api-url'), {
                type: 'post',
                data: {source: this.getAttribute("data-source")},
                success: function (data, textStatus) {
                    timing($('.hqyzm'));
                    var message = '验证码发送失败，请重试。';
                    if (textStatus === 'success') {
                        var ret = data.ret;
                        if (ret) {
                            message = '验证码已发送到手机号' + data['phone_no']
                        } else {
                            var code = data.code;
                            if (code === 450) {
                                message = "请到<a href='http://account.lvye.cn'>用户中心</a>绑定手机号, 然后重新登录";
                            }
                        }
                    }
                    $('.verification-code.warn').html(message);
                },
                error: function () {
                    $('.hqyzm').removeAttr('disabled').attr('value', '重新获取');
                    $('.verification-code.warn').html('验证码获取失败，请重新获取');
                }
            });
        } else {
            $("#request_verification_code-"+this.getAttribute("data-source")).attr("value", "yes");
            $("#submit-"+this.getAttribute("data-source")).click();
        }
    });


    if ($('.hqyzm')[0].getAttribute('data-verified') === "yes") {
        $('.hqyzm')[0].click();
    }
});