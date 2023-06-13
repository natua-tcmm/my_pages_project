// ロード時に検索窓を選択状態にする
window.onload = function () {
    $("#query").select();
};

// 難易度切り替え
var display_dif_index = 1;
$("#change_dif").on("click", function () {
    display_dif_index += 1;

    if (display_dif_index % 3 == 0) {
        $(".constdisp_expert").css("display", "flex");
        $(".constdisp_master").css("display", "none");
        $(".constdisp_ultima").css("display", "none");
    }
    else if (display_dif_index % 3 == 1) {
        $(".constdisp_expert").css("display", "none");
        $(".constdisp_master").css("display", "flex");
        $(".constdisp_ultima").css("display", "none");
    }
    else if (display_dif_index % 3 == 2) {
        $(".constdisp_expert").css("display", "none");
        $(".constdisp_master").css("display", "none");
        $(".constdisp_ultima").css("display", "flex");
    }

});

// クリアボタンの処理
$("#clear-button").on("click", function (e) {
    $("#query").val("");
    $("#query").select();
    search_songs(e, type);
});

// 機種選択
var type = "c"
$("#type-c").on("click", function (e) {
    if ($("#type-c").prop("checked")) {
        type = "c";
    }
    else {
        type = "o";
    }
    search_songs(e, type);
    setTimeout(() => { $("#query").select(); }, 5);
});
$("#type-o").on("click", function (e) {
    if ($("#type-o").prop("checked")) {
        type = "o";
    }
    else {
        type = "c";
    }
    search_songs(e, type);
    setTimeout(() => { $("#query").select(); }, 5);
});

// --------------------------------

// 検索ワードの送信
$('#ajax-search').on('submit input', function (e) {
    // console.log($("#is_use_name").prop('checked'));
    search_songs(e, type);
});

// 楽曲検索
var search_songs = function (e, type) {

    $("#loading_text").css("display", "");

    // 通常の送信処理を止める
    event.preventDefault();

    // 送信する
    $.ajax({
        'url': send_url,
        'type': 'POST',
        'data': {
            "csrfmiddlewaretoken": csrfmiddlewaretoken,
            'query': $('#query').val(),
            "is_use_name": $("#is_use_name").prop('checked'),
            "is_use_reading": $("#is_use_reading").prop('checked'),
            "is_use_artists": $("#is_use_artists").prop('checked'),
            "type": type
        },
        'dataType': 'json',
    })
        //成功時
        .done(function (response) {

            if (response.update_log.length > 2)
                console.log(response.update_log);
            else {
                // 今表示されてるやつを消す
                $(".song-group-item").remove();
                // 新しく表示する
                for (var i = 0; i < response.search_response.length; i++)
                    $("#post-songs").prepend(response.search_response[i]);

                $("#search_hit_text").html("検索結果 : " + response.search_hit_count + " 件");
            }

            $("#loading_text").css("display", "none");

        })
        //失敗時
        .fail(function () {
            // 今表示されてるやつを消す
            $(".song-group-item").remove();
        })

}
