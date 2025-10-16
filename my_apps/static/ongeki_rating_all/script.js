window.addEventListener('DOMContentLoaded', function(){

    // osl_idをlocalStrageとやりとり
    var ls_osl_id = localStorage.getItem("ongeki_rating_all__osl_id");
    if (ls_osl_id !== null) {
        $("#osl-id").val(ls_osl_id);
    }


});

// 実行ボタンが押されたとき
$("#calc-button").on("click",function(e){

    var osl_id = $("#osl-id").val();

    if(!isNaN(osl_id)&&osl_id.length>0){

        osl_id = Number(osl_id);

        var music_rate_type = $("#music-rate-type").val();

        // localStrageにIDを保存
        localStorage.setItem("ongeki_rating_all__osl_id",osl_id);

        // 送信
        ajax_send(e, osl_id, music_rate_type)
        .done(function (response) {

            localStorage.setItem("ongeki_rating_all__osl_id",osl_id);

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
        console.log("数値以外が入力されています");
    }

});


var ajax_send = function (e, osl_id, music_rate_type) {

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
            "osl_id": osl_id,
            "music_rate_type": music_rate_type,
            "request_time": new Date().getTime(),
        },
        'dataType': 'json',
    })

}
