$(function () {
    $(".loginBtn .sx").hover(function () {
        $(this).find("ul").stop().fadeIn();
    }, function () {
        $(this).find("ul").stop().fadeOut();
    });
    $(".loginBtn .yh").click(function () {
        $(this).find("ul").stop().fadeIn();
    });

    function clearErrors() {
        $('#amount').removeClass('orangetxk');
        $('#amount').parent().find('.mistake').remove();
        $('#comment').removeClass('orangetxk');
        $('#comment').parent().find('.mistake').remove();
    }

    var amountPattern = /^\d+(.\d{1,2})?$/ig;

    function validate() {
        var errors = {};
        var amount = $('#amount').val();
        if (!amount || !amount.match(amountPattern) || amount <= 0) {
            errors['amount'] = '请输入数字，小数点后最多2位， 例如"8.88"';
        }
        var comment = $('#comment').val();
        if (!comment) {
            errors['comment'] = '请提供备注信息';
        }
        if (comment.length > 140) {
            errors['comment'] = '备注不能超过140个字';
        }
        return errors;
    }

    function showErrorMessages(errors) {
        if (!!errors['amount']) {
            $('#amount').addClass('orangetxk');
            var error = $('<em class="mistake"></em>').text(errors['amount']);
            $('#amount').parent().append(error);
        }
        if (!!errors['comment']) {
            $('#comment').addClass('orangetxk');
            var error = $('<em class="mistake"></em>').text(errors['comment']);
            $('#comment').parent().append(error);
        }
    }

    function updateConfirmInfomation() {
        var amount = $('#amount').val();
        var comment = $('#comment').val();
        $('.confirm .amount').text(amount + '元');
        $('.confirm .bz').text(comment);
    }

    /*提交*/
    $(".payoffRight .line .tijiaoLayer").click(function () {
        clearErrors();
        var errors = validate();
        if (!$.isEmptyObject(errors)) {
            showErrorMessages(errors);
            return;
        }
        updateConfirmInfomation();
        $(".bgLayer,.confirm").stop().fadeIn();
    });
    $(".confirm a.close").click(function () {
        $(".bgLayer,.confirm").stop().fadeOut();
    });
    $(".finaline button").click(function () {
        $(".bgLayer,.confirm").stop().fadeOut();
        $("#main").showLoading();
    });
});
