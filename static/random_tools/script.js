// IDをformは#ajax-xxx、queryは#query-xxxにする

// 送信時の処理
$('#ajax-unicode').on('submit', function (e) {

    ajax_send(e, "unicode",$('#query-unicode').val())
    .done(function (response) {

        $("#loading-text").css("display", "none");
        console.log(response.result);

        // 今表示されてるやつを消す
        $("#unicode-table-wrapper").children().remove();

        // 新しく表示する
        $("#unicode-table-wrapper").prepend(response.result);

    })
    .fail(function () {
        alert("Ajax通信に失敗しました(´・ω・`)")
    });

});



// ------------------------

var ajax_send = function (e, type, query) {

    $("#loading-text").css("display", "");

    // 通常の送信処理を止める
    if (e) {
        e.preventDefault();
    }

    // 送信する
    return $.ajax({
        'url': send_url,
        'type': 'POST',
        'data': {
            "csrfmiddlewaretoken": csrfmiddlewaretoken,
            "query": query,
            "request_time": new Date().getTime(),
            "type":type,
        },
        'dataType': 'json',
    })

}

// ------------------------

// 一時だし寝るか
$("#itijidashi-neruka").on("click",function(){

    // ツイート生成
    var base_url = "https://twitter.com/intent/tweet";
    var text = "1時だし寝るか(  ･᷄ᯅ･᷅ )";
    var tweetLink = base_url + "?text=" + encodeURIComponent(text);
    window.open(tweetLink);

});
