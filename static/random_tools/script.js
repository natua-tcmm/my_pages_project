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
    var tweet_link = base_url + "?text=" + encodeURIComponent(text);
    window.open(tweet_link);

});

// ------------------------

// ついったー検索

$("#xs-ok-btn").on("click",function(){

    var keyword_and = $("#xs-keyword-and").val();
    var xs_accout_from = $("#xs-account-from").val();
    var xs_accout_from_isnot = $("#xs-account-from-isnot").prop('checked');
    var xs_accout_to = $("#xs-account-to").val();
    var xs_accout_to_isnot = $("#xs-account-to-isnot").prop('checked');
    var xs_media_option = $("#xs-media-option").val();

    var q = "";
    if(keyword_and.length>0) q += keyword_and+" ";
    if(xs_accout_from.length>0) q += "-".repeat(xs_accout_from_isnot) + "from:"+xs_accout_from+" ";
    if(xs_accout_to.length>0) q += "-".repeat(xs_accout_to_isnot) + "to:"+xs_accout_to+" ";
    if(xs_media_option.length>0) q += "filter:"+xs_media_option+" ";

    console.log(q)

    // URL生成
    var base_url = "https://twitter.com/search";
    var x_search_link = base_url + "?q=" + encodeURIComponent(q);
    window.open(x_search_link);

});
