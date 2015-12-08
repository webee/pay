var requestRunning = false;

function update_available_balance(callback) {
    if (requestRunning) {
        return;
    }

    requestRunning = true;
    var available_balance = $("#available_balance")[0];
    $.getJSON(available_balance.getAttribute('data-api-url'))
        .done(function (res) {
            $("#available_balance").html(res.available_balance);
        }).complete(function() {
            requestRunning = false;
            if (callback != null) {
                callback();
            }
        });
}

$(document).ready(function () {
    var tabs = ['#total_tx', '#in_tx', '#out_tx', '#tx_in_tx', '#tx_out_tx'];

    function clear_class(ids) {
        for (var i = 0; i < ids.length; i++) {
            var cid = ids[i];
            $(cid).attr('class', '');
        }
    }

    function get_cur_tab() {
        return $("#tx_type_tabs")[0].getAttribute("data-cur");
    }

    function gen_activate_tab_cb(t) {
        return function() {
            var ts = [];
            for (var i = 0; i < tabs.length; i++) {
                if (tabs[i] != t) {
                    ts.push(tabs[i]);
                }
            }
            $("#tx_type_tabs")[0].setAttribute("data-cur", t);
            $(t).attr('class', 'cur');
            clear_class(ts);

            $("#total_tx").click(function() {
                get_tx_list({role: ''}, gen_activate_tab_cb('#total_tx'))
            });

            $("#in_tx").click(function() {
                get_tx_list({role: 'TO'}, gen_activate_tab_cb('#in_tx'))
            });

            $("#out_tx").click(function() {
                get_tx_list({role: 'FROM'}, gen_activate_tab_cb('#out_tx'))
            });

            $("#tx_in_tx").click(function() {
                get_tx_list({role: 'TX_TO'}, gen_activate_tab_cb('#tx_in_tx'))
            });

            $("#tx_out_tx").click(function() {
                get_tx_list({role: 'TX_FROM'}, gen_activate_tab_cb('#tx_out_tx'))
            });
        }
    }

    function handle_pager(params, callback) {
        var pager = $("#tx_list_pager")[0];
        if (pager == undefined) {
            return;
        }

        var page_no = Number(pager.getAttribute("data-page-no"));
        var page_count = Number(pager.getAttribute("data-page-count"));
        var prev_page_no = page_no - 1;
        var next_page_no = page_no + 1;
        if (prev_page_no < 1) {
            prev_page_no = 1;
        }
        if (next_page_no > page_count) {
            next_page_no = page_count
        }

        $("#tx_list_first").on("click", function() {
            $.extend(params, {page_no: 1});
            get_tx_list(params, callback)
        });
        $("#tx_list_last").on("click", function() {
            $.extend(params, {page_no: page_count});
            get_tx_list(params, callback)
        });
        $("#tx_list_prev").on("click", function() {
            $.extend(params, {page_no: prev_page_no});
            get_tx_list(params, callback)
        });
        $("#tx_list_next").on("click", function() {
            $.extend(params, {page_no: next_page_no});
            get_tx_list(params, callback)
        });
    }

    function handle_search_bt(params, callback) {
        $("#tx_search_bt").on("click", function() {
            var q = $("#tx_search_q")[0].value;
            $.extend(params, {q: q, page_no: 1});
            get_tx_list(params, callback);
        });
    }

    function get_tx_list(params, callback) {
        if (requestRunning) {
            return;
        }

        requestRunning = true;
        var tx_list = $("#tx_list")[0];
        $.get(tx_list.getAttribute('data-api-url'), params)
            .done(function (data) {
                $("#tx_list").html(data);
                if (callback != null) {
                    callback();
                }

                handle_pager(params, callback);
                handle_search_bt(params, callback);
            })
            .complete(function (){
                requestRunning = false;
            });
    }

    // update available balance.
    update_available_balance(function() {
        // activate total.
        get_tx_list({role: '', page_no: 1}, gen_activate_tab_cb('#total_tx'))
    });
});