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
    $(".payoffRight .line .tijiaoLayer").click(function () {
        $(".bgLayer,.confirm").stop().fadeIn();
    });
    $(".confirm a.close,.finaline button").click(function () {
        $(".bgLayer,.confirm").stop().fadeOut();
    });
});
