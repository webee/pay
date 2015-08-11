function update_balance() {
    $.getJSON('/balance')
        .done(function (res) {
            $("#balance").html(res.balance);
        });
}

$(document).ready(function () {
    var tabs = ['#total_tx', '#in_tx', '#out_tx', '#withdraw_tx'];

    function clear_class(ids) {
        for (var i = 0; i < ids.length; i++) {
            var cid = ids[i];
            $(cid).attr('class', '');
        }
    }

    function gen_activate_tab_cb(t) {
        return function() {
            var ts = []
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i] != t) {
                    ts.push(tabs[i]);
                }
            }
            $(t).attr('class', 'cur');
            clear_class(ts)

            $("#total_tx").click(function() {
                get_tx_list({}, gen_activate_tab_cb('#total_tx'))
            });

            $("#in_tx").click(function() {
                get_tx_list({side: 'CREDIT'}, gen_activate_tab_cb('#in_tx'))
            });

            $("#out_tx").click(function() {
                get_tx_list({side: 'DEBIT'}, gen_activate_tab_cb('#out_tx'))
            });

            $("#withdraw_tx").click(function() {
                get_tx_list({tp: 'WITHDRAW'}, gen_activate_tab_cb('#withdraw_tx'))
            });
        }
    }

    function handle_pager(params, callback) {
        var pager = $("#tx_list_pager")[0];
        var page_no = Number(pager.dataset["pageNo"]);
        var page_count = Number(pager.dataset["pageCount"]);
        var prev_page_no = page_no - 1;
        var next_page_no = page_no + 1;
        if (prev_page_no < 1) {
            prev_page_no = 1;
        }
        if (next_page_no > page_count) {
            next_page_no = page_count
        }

        $("#tx_list_first").on("click", function() {
            $.extend(params, {page_no: 1})
            get_tx_list(params, callback)
        });
        $("#tx_list_last").on("click", function() {
            $.extend(params, {page_no: page_count})
            get_tx_list(params, callback)
        });
        $("#tx_list_prev").on("click", function() {
            $.extend(params, {page_no: prev_page_no})
            get_tx_list(params, callback)
        });
        $("#tx_list_next").on("click", function() {
            $.extend(params, {page_no: next_page_no})
            get_tx_list(params, callback)
        });
    }
    function get_tx_list(params, callback) {
        $.get('/transaction_list', params)
            .done(function (data) {
                $("#tx_list").html(data);
                if (callback != null) {
                    callback();
                }

                handle_pager(params, callback);
            });
    }

    // update balance.
    update_balance();
    setInterval("update_balance()", 10000);

    // activate total.
    get_tx_list({}, gen_activate_tab_cb('#total_tx'))
});