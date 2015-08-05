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

    $('.province').change(function () {
        var selectedProvince = $(this).children('option:selected').text();
        $.get('/data/provinces/' + selectedProvince + '/cities', function (result, textStatus) {
            if (textStatus === 'success') {
                var citySelect = $('.city');
                citySelect.empty();
                $.each(result.data, function (index, city) {
                    citySelect.append($('<option></option>').attr('value', city[1]).text(city[0]));
                });
            }
        });
    });
});