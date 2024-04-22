window.addEventListener('DOMContentLoaded', function(){

    // osl_idをlocalStrageとやりとり
    var ls_osl_id = localStorage.getItem("ongeki_op__osl_id");
    if (ls_osl_id !== null) {
        $("#osl-id").val(ls_osl_id);
    }


});

// 実行ボタンが押されたとき
$("#calc-button").on("click",function(e){

    var osl_id = $("#osl-id").val();

    if(!isNaN(osl_id)&&osl_id.length>0){

        osl_id = Number(osl_id);
        var classification = $("#classification").val();
        var display_format = $("#display-format").val();
        // console.log(type)

        // localStrageにIDを保存
        localStorage.setItem("ongeki_op__osl_id",osl_id);

        // 送信
        ajax_send(e, osl_id, classification, display_format)
        .done(function (response) {

            localStorage.setItem("ongeki_op__osl_id",osl_id);

            $("#loading-text").css("display", "none");
            // console.log(response);

            // op概要
            // 今表示されてるやつを消す
            $("#op_summary").children().remove();
            $("#op_card").children().remove();

            // 新しく表示する
            $("#op_summary").prepend(response.op_summary_html);
            $("#op_card").prepend(response.op_card_html);

        })
        .fail(function () {
            alert("Ajax通信に失敗しました(´・ω・`)")
        });

    }
    else{
        console.log("数値以外がにゅうりょくされています");
    }

});


var ajax_send = function (e, osl_id, classification, display_format) {

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
            "classification":classification,
            "display_format":display_format,
            "request_time": new Date().getTime(),
        },
        'dataType': 'json',
    })

}
