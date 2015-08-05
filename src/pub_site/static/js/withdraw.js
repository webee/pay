$(function () {
    $(function () {
        $(".loginBtn .sx").hover(function () {
            $(this).find("ul").stop().fadeIn();
        }, function () {
            $(this).find("ul").stop().fadeOut();
        });
        $(".loginBtn .yh").click(function () {
            $(this).find("ul").stop().fadeIn();
        });

        /*提交*/
        $(".cardInform em.choiceblue").click(function () {
            $(".bgLayer,.choiceLayer").stop().fadeIn();
        });

        $(".choiceLayer a.close,.choiceLayer .stepBtn").click(function () {
            $(".bgLayer,.choiceLayer").stop().fadeOut();
        });

        /*选择银行卡*/
        $(".kindsCard li .bankcard").click(function () {
            $(this).parent("li").addClass("cur").siblings().removeClass("cur");
            var imgUrl = $(this).find("img").attr("src");
            var bankName = $(this).find(".bankname").html();
            var cardNum = $(this).find(".cardNum").html();
            var cardId = $(this).find(".cardId").val();
            $(".choiceLayer .stepBtn").click(function () {
                $(".bgLayer,.choiceLayer").stop().fadeOut();
                $(".cardInform img").attr("src", imgUrl);
                $(".cardInform .bankcard .bankname").html(bankName);
                $(".cardInform .bankcard .cardNum").html(cardNum);
                $("#selected_bankcard").val(cardId);
            });
        });
    })
});