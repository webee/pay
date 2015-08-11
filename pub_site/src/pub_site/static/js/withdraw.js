$(function () {
    $(".loginBtn .sx").hover(function () {
        $(this).find("ul").stop().fadeIn();
    }, function () {
        $(this).find("ul").stop().fadeOut();
    });
    $(".loginBtn .yh").click(function () {
        $(this).find("ul").stop().fadeIn();
    });

    function synchronizePreferredCardOnPanel() {
        $('.kindsCard li').removeClass('cur');
        var originPreferredCardId = $("#selected_bankcard").val();
        $('.kindsCard').find('input[value="' + originPreferredCardId + '"]').parent().parent().addClass('cur');
    }

    /*提交*/
    $(".cardInform em.choiceblue").click(function () {
        synchronizePreferredCardOnPanel();
        $(".bgLayer,.choiceLayer").stop().fadeIn();
    });

    $(".choiceLayer a.close").click(function () {
        $(".bgLayer,.choiceLayer").stop().fadeOut();
        synchronizePreferredCardOnPanel();
    });

    /*选择银行卡*/
    $(".kindsCard li .bankcard").click(function () {
        $(this).parent("li").addClass("cur").siblings().removeClass("cur");
    });

    $(".choiceLayer .stepBtn").click(function () {
        var selectedCard = $('.kindsCard li.cur');
        var imgUrl = selectedCard.find("img").attr("src");
        var bankName = selectedCard.find(".bankname").html();
        var cardNum = selectedCard.find(".cardNum").html();
        var cardId = selectedCard.find(".cardId").val();
        $(".cardInform img").attr("src", imgUrl);
        $(".cardInform .bankcard .bankname").html(bankName);
        $(".cardInform .bankcard .cardNum").html(cardNum);
        $("#selected_bankcard").val(cardId);
        $(".bgLayer,.choiceLayer").stop().fadeOut();
    });

    $('#submit').click(function () {
        $('#main').showLoading();
    });
});