window.addEventListener('DOMContentLoaded', function(){

    // rec_idをlocalStrageとやりとり
    var ls_rec_id = localStorage.getItem("chunithm_rating_all__rec_id");
    if (ls_rec_id !== null) {
        $("#rec-id").val(ls_rec_id);
    }


});

// 実行ボタンが押されたとき
$("#calc-button").on("click",function(e){

    var rec_id = $("#rec-id").val();

    if(rec_id.length>0){

        // rec_id = Number(rec_id);
        // console.log(type)

        // localStrageにIDを保存
        localStorage.setItem("chunithm_rating_all__rec_id",rec_id);

        // 送信
        ajax_send(e, rec_id)
        .done(function (response) {

            localStorage.setItem("chunithm_rating_all__rec_id",rec_id);

            $("#loading-text").css("display", "none");
            // console.log(response);

            // op概要
            // 今表示されてるやつを消す
            $("#summary").children().remove();
            $("#result").children().remove();

            // 新しく表示する
            $("#summary").prepend(response.summary);
            $("#result").prepend(response.result);

        })
        .fail(function () {
            alert("Ajax通信に失敗しました(´・ω・`)\nページを再読み込みしてください。")
        });

    }
    else{
        console.log("にゅうりょくしてね");
    }

});


var ajax_send = function (e, rec_id) {

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
            "rec_id": rec_id,
            "request_time": new Date().getTime(),
        },
        'dataType': 'json',
    })

}
