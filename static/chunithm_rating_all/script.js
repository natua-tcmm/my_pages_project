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

        var display_format = $("#display-format").val();

        // localStrageにIDを保存
        localStorage.setItem("chunithm_rating_all__rec_id",rec_id);

        // 送信
        ajax_send(e, rec_id, display_format)
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
        .fail(function (jqXHR, textStatus, errorThrown) {
            let date = new Date();
            var d1 = date.getFullYear() + '/' + ('0' + (date.getMonth() + 1)).slice(-2) + '/' +('0' + date.getDate()).slice(-2) + ' ' +  ('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2) + ':' + ('0' + date.getSeconds()).slice(-2) + '.' + date.getMilliseconds();
            alert("エラーが発生しました。ページを再読み込みして再実行してください。\n何度も発生する場合は、お手数ですが次の画面のスクリーンショットを管理者(@natua_tcmm)へ報告してください。");
            alert(+jqXHR.status+" / "+textStatus+" / "+errorThrown+"\ntime:"+d1);
        });

    }
    else{
        console.log("にゅうりょくしてね");
    }

});


var ajax_send = function (e, rec_id, display_format) {

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
            "display_format":display_format,
            "request_time": new Date().getTime(),
        },
        'dataType': 'json',
    })

}
