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
        if (this.data['verified'] === "yes") {
            $(this).attr('disabled', 'disabled').attr('value', '正在获取');
            $('.verification-code.warn').html('');
            $.ajax(this.data['apiUrl'], {
                type: 'post',
                data: {source: this.data["source"]},
                success: function (data, textStatus) {
                    timing($('.hqyzm'));
                    var message = textStatus === 'success'
                        ? '验证码已发送到手机号' + data['phone_no']
                        : '验证码发送失败，请重试。';
                    $('.verification-code.warn').html(message);
                },
                error: function () {
                    $('.hqyzm').removeAttr('disabled').attr('value', '重新获取');
                    $('.verification-code.warn').html('验证码获取失败，请重新获取');
                }
            });
        } else {
            $("#request_verification_code-"+this.data["source"]).attr("value", "yes");
            $("#submit-"+this.data["source"]).click();
        }
    });


    if ($('.hqyzm')[0].data['verified'] === "yes") {
        $('.hqyzm')[0].click();
    }
});