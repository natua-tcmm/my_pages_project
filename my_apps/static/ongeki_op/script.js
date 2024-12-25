window.addEventListener('DOMContentLoaded', function(){

    // osl_idをlocalStrageとやりとり
    var ls_osl_id = localStorage.getItem("ongeki_op__osl_id");
    if (ls_osl_id !== null) {
        $("#osl-id").val(ls_osl_id);
    }


});

$(document).on("change", "#classification", function() {
    console.log("classification changed");
    var selectedValue = $(this).val();
    var displayclass = ".cat-" + selectedValue;
    var classNameList = [".cat-level", ".cat-category", ".cat-version", ".cat-const"];
    for (var i = 0; i < classNameList.length; i++) {
        $(classNameList[i]).css("display", "none");
    }
    $(displayclass).css("display", "");
});

// 実行ボタンが押されたとき
$("#calc-button").on("click",function(e){

    var osl_id = $("#osl-id").val();

    if(!isNaN(osl_id)&&osl_id.length>0){

        osl_id = Number(osl_id);
        var display_format = $("#display-format").val();

        // localStrageにIDを保存
        localStorage.setItem("ongeki_op__osl_id",osl_id);

        var ls_op_before = localStorage.getItem("ongeki_op__op_before");

        // 送信
        ajax_send(e, osl_id, display_format, ls_op_before)
        .done(function (response) {

            // 楽曲情報が見つからなかった場合の通知
            if (response.invalid_music_list.length > 0) {
                alert("以下の楽曲の情報が見つからなかったため、楽曲が存在しないものとして集計しています。\n楽曲情報が追加されるまでしばらくお待ち下さい。\n\n" + response.invalid_music_list.join("\n"));
            }

            // localStrageに情報を保存
            localStorage.setItem("ongeki_op__osl_id",osl_id);
            localStorage.setItem("ongeki_op__op_before",response.op_new)

            // ローディング非表示
            $("#loading-text").css("display", "none");

            // op概要
            // 今表示されてるやつを消す
            $("#op_summary").children().remove();
            $("#op_card").children().remove();

            // 新しく表示する
            $("#op_summary").prepend(response.op_summary_html);
            $("#op_card").prepend(response.op_card_html);

            // 簡易表示時プロパティ変更
            if(display_format=="2"){
                document.documentElement.style.setProperty("--graph-height","15px");
            }

            // カテゴリの表示
            var classNameList = [".cat-level", ".cat-category", ".cat-version", ".cat-const"];
            for (var i = 0; i < classNameList.length; i++) {
                $(classNameList[i]).css("display", "none");
            }
            $(".cat-category").css("display", "");

        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            let date = new Date();
            var d1 = date.getFullYear() + '/' + ('0' + (date.getMonth() + 1)).slice(-2) + '/' +('0' + date.getDate()).slice(-2) + ' ' +  ('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2) + ':' + ('0' + date.getSeconds()).slice(-2) + '.' + date.getMilliseconds();
            alert("エラーが発生しました。ページを再読み込みして再実行してください。\n何度も発生する場合は、お手数ですが次の画面のスクリーンショットを管理者(@natua_tcmm)へ報告してください。");
            alert(+jqXHR.status+" / "+textStatus+" / "+errorThrown+"\ntime:"+d1);
        });

    }
    else{
        console.log("数値以外が入力されています。");
    }

});


var ajax_send = function (e, osl_id, display_format, ls_op_before) {

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
            "op_before": ls_op_before,
            "display_format":display_format,
            "request_time": new Date().getTime(),
        },
        'dataType': 'json',
    })

}
