// 検索ワードの送信
$('#ajax-search').on('submit input', function (e) {

    $("#loading_text").css("display", "");

    // 通常の送信処理を止める
    if (e) {
        e.preventDefault();
    }

    // 送信する
    $.ajax({
        'url': send_url,
        'type': 'POST',
        'data': {
            "csrfmiddlewaretoken": csrfmiddlewaretoken,
            'query': $('#query').val(),
            "request_time": new Date().getTime(),
        },
        'dataType': 'json',
    })
        //成功時
        .done(function (response) {

            console.log(response.query);

            $("#loading_text").css("display", "none");

        })
        //失敗時
        .fail(function () {

        })

});
