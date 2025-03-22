// ロード時
window.onload = function () {

    // 検索ボックスにフォーカス
    window.setTimeout(function (e) {
        $("#query").select();
        search_songs(e, "c", "s");
    }, 10);

    // レンジスライダーの初期化
    $("#slider-bpm").ionRangeSlider({
        type: "double",
        min: 100,
        max: 300,
        from: 30,
        to: 500,
        step: 10,
        prefix: "BPM",
        tooltip: "auto",
    });
    $("#slider-notes").ionRangeSlider({
        type: "double",
        min: 1000,
        max: 4000,
        from: 1000,
        to: 4000,
        step: 100,
        postfix: "Notes",
        tooltip: "auto",
        prettify: function (num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "");
        }
    });
    $("#slider-wrapper-bpm").css("display", "none");
    $("#slider-wrapper-notes").css("display", "none");

};

// スライダーの表示・非表示
$("#is_use_bpm").on("change", function () {
    if ($(this).prop('checked')) {
        $("#slider-wrapper-bpm").css("display", "");
    } else {
        $("#slider-wrapper-bpm").css("display", "none");
    }
});
$("#is_use_notes").on("change", function () {
    if ($(this).prop('checked')) {
        $("#slider-wrapper-notes").css("display", "");
    } else {
        $("#slider-wrapper-notes").css("display", "none");
    }
});

// LUNATICオプションの表示・非表示
$("#is_use_lunatic_option").on("change", function () {
    if ($(this).prop('checked')) {
        $("#select-lunatic").css("display", "");
    } else {
        $("#select-lunatic").css("display", "none");
    }
});

// 難易度切り替え
var display_dif_index = 1;
var change_dif = function () {

    if (display_dif_index % 3 == 0) {
        $(".constdisp_expert").css("display", "flex");
        $(".constdisp_master").css("display", "none");
        $(".constdisp_ultima").css("display", "none");
        $(".constdisp_lunatic").css("display", "none");
        $(".constdisp_expert_inline").css("display", "inline");
        $(".constdisp_master_inline").css("display", "none");
        $(".constdisp_ultima_inline").css("display", "none");
        $(".constdisp_lunatic_inline").css("display", "none");
    }
    else if (display_dif_index % 3 == 1) {
        $(".constdisp_expert").css("display", "none");
        $(".constdisp_master").css("display", "flex");
        $(".constdisp_ultima").css("display", "none");
        $(".constdisp_lunatic").css("display", "none");
        $(".constdisp_expert_inline").css("display", "none");
        $(".constdisp_master_inline").css("display", "inline");
        $(".constdisp_ultima_inline").css("display", "none");
        $(".constdisp_lunatic_inline").css("display", "none");
    }
    else if (display_dif_index % 3 == 2) {
        $(".constdisp_expert").css("display", "none");
        $(".constdisp_master").css("display", "none");
        if (type === "c") {
            $(".constdisp_ultima").css("display", "flex");
            $(".constdisp_lunatic").css("display", "none");
            $(".constdisp_ultima_inline").css("display", "inline");
            $(".constdisp_lunatic_inline").css("display", "none");
        }
        else {
            $(".constdisp_ultima").css("display", "none");
            $(".constdisp_lunatic").css("display", "flex");
            $(".constdisp_ultima_inline").css("display", "none");
            $(".constdisp_lunatic_inline").css("display", "inline");
        }
        $(".constdisp_ultima").css("display", "flex");
        $(".constdisp_lunatic").css("display", "flex");
        $(".constdisp_expert_inline").css("display", "none");
        $(".constdisp_master_inline").css("display", "none");
    }
}
// 難易度切り替えボタンの処理
$("#change_dif").on("click", function () {

    display_dif_index += 1;
    change_dif();

});

// クリアボタンの処理
$("#clear-button").on("click", function (e) {
    $("#query").val("");
    $("#query").select();

    // 空表示を取得
    search_songs(e, type, disp);
});

var disp = "s", type = "c";

// 表示方式の変更（idが"disp-"で始まるラジオボタン）
$("input[id^='disp-']").on("change", function (e) {

    // 表示方式の変更
    disp = $(this).attr("id") === "disp-full" ? "f" : "s";

    // 詳細オプションの表示
    $("#detail-option").css("display", disp === "f" ? "" : "none");

    // 検索
    $(".song-group-item").remove();
    search_songs(e, type, disp);
    setTimeout(() => { $("#query").select(); }, 5);

});

// 機種の変更（idが"type-"で始まるラジオボタン）
$("input[id^='type-']").on("change", function (e) {

    type = $(this).attr("id") === "type-o" ? "o" : "c";

    // "/ジャンル名"文字列の表示
    $("#subname_text").css("display", type === "o" ? "" : "none");

    // ボーナストラック表示の変更
    $("#is-disp-bonus-wrapper").css("display", type === "o" ? "" : "none");

    // Lunaticオプション表示の変更
    $("#is_use_lunatic_option-wrapper").css("display", type === "o" ? "" : "none");

    // 難易度表示の変更
    display_dif_index = 1;
    change_dif();

    // 検索
    $(".song-group-item").remove();
    search_songs(e, type, disp);
    setTimeout(() => { $("#query").select(); }, 5);
});


// --------------------------------

// 譜面画像ボタン
// ページ全体に対して、クラス fumenbtn を持つボタンのクリックイベントをデリゲートで処理
$(document).on('click', '.fumenbtn', function() {
    var dif = $(this).data('dif');
    var songFumenId = Number($(this).data('songfumenid'));
    var type = $(this).data('type');
    var url = '';

    // CHUNITHMの場合
    if( type === "c" ){
        if (dif === 'e') {
            // Expert用
            url = 'https://www.sdvx.in/chunithm/' +
                  (songFumenId / 1000).toFixed().padStart(2, '0') + '/' +
                  songFumenId.toFixed().padStart(5, '0') + 'exp.htm';
        } else if (dif === 'm' || dif === 'm_fallback') {
            // Master用
            url = 'https://www.sdvx.in/chunithm/' +
                  (songFumenId / 1000).toFixed().padStart(2, '0') + '/' +
                  songFumenId.toFixed().padStart(5, '0') + 'mst.htm';
        } else if (dif === 'u') {
            // Ultima用
            url = 'https://www.sdvx.in/chunithm/ult/' +
                  songFumenId.toFixed().padStart(5, '0') + 'ult.htm';
        }
    }
    // オンゲキの場合
    else if( type === "o" ){
        if (dif === 'e') {
            // Expert用
            url = 'https://www.sdvx.in/ongeki/' +
                  (songFumenId / 1000).toFixed().padStart(2, '0') + '/' +
                  songFumenId.toFixed().padStart(5, '0') + 'exp.htm';
        } else if (dif === 'm' || dif === 'm_fallback') {
            // Master用
            url = 'https://www.sdvx.in/ongeki/' +
                  (songFumenId / 1000).toFixed().padStart(2, '0') + '/' +
                  songFumenId.toFixed().padStart(5, '0') + 'mst.htm';
        }
        else if (dif === 'l' || dif === 'l_fallback') {
            // Lunatic用
            url = 'https://www.sdvx.in/ongeki/luna/' +
                  songFumenId.toFixed().padStart(5, '0') + 'luna.htm';
        }
     }

    window.open(url);
});


// --------------------------------

// 検索ステータス
var request_count = 0;
var response_count = 0;
var invalid_response_count = 0;

// 検索ステータスを更新する
var update_search_status = function () {
    $("#search-status").html("↑" + request_count + "↓" + response_count + "(-" + invalid_response_count + ")");
}

// 検索ワードを変更した際に送信
$('#ajax-search').on('submit input', function (e) {
    // 検索
    search_songs(e, type, disp);
});

// スライダー値を変更した際に送信
setTimeout(function () {
    $("#slider-bpm").on("change", function (e) {
        search_songs(e, type, disp);
    });
    $("#slider-notes").on("change", function (e) {
        search_songs(e, type, disp);
    });
}, 1000);

// --------------------------------

// debounce関数
function debounce(func, delay) {
    var timeout;
    return function(...args) {
        // 前のタイマーがあればクリア
        if (timeout) {
            clearTimeout(timeout);
        }
        // delayミリ秒後にfuncを実行
        timeout = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

// 楽曲検索のリクエスト
var currentRequest = null;
var search_songs = debounce( function (e, type, disp) {

    // 検索ステータスを更新
    request_count++;
    update_search_status();

    $("#loading_text").css("display", "");

    // 通常の送信処理を止める
    if (e) {
        e.preventDefault();
    }

    // もし既にリクエスト中ならキャンセルする
    if (currentRequest) {
        currentRequest.abort();
    }

    // 送信する
    currentRequest =  $.ajax({
        'url': send_url,
        'type': 'POST',
        'data': {
            "csrfmiddlewaretoken": csrfmiddlewaretoken,
            'query': $('#query').val(),
            "search_settings":{
                "is_use_name": $("#is_use_name").prop('checked'),
                "is_use_artists": $("#is_use_artists").prop('checked'),
                "is_use_nd": $("#is_use_nd").prop('checked'),
                "is_use_bpm": $("#is_use_bpm").prop('checked'),
                "bpm_from": $("#slider-bpm").data("ionRangeSlider").result.from,
                "bpm_to": $("#slider-bpm").data("ionRangeSlider").result.to,
                "is_use_notes": $("#is_use_notes").prop('checked'),
                "notes_from": $("#slider-notes").data("ionRangeSlider").result.from,
                "notes_to": $("#slider-notes").data("ionRangeSlider").result.to,
                "is_disp_bonus": $("#is-disp-bonus").prop('checked'),
                "is_use_lunatic_option": $("#is_use_lunatic_option").prop('checked'),
                "lunatic_option": $("#select-lunatic").val(),
            },
            "type": type,
            "display_type": disp,
            "request_time": new Date().getTime(),
        },
        'dataType': 'json',
        "success" : function(response) {

            // 今表示されてるやつを消す
            $(".song-group-item").remove();

            // 新しく表示する
            for (var i = 0; i < response.search_response.length; i++)
                $("#post-songs").prepend(response.search_response[i]);

            $("#search_hit_text").html("検索結果 : " + response.search_hit_count + " 件");
            // $("#search-query-list-display").html(response.search_query_list);

            $("#loading_text").css("display", "none");

        },
        "error" : function(xhr, status, error) {
            if (status !== "abort") {
                // 今表示されてるやつを消す
                $(".song-group-item").remove();
                $("#loading_text").css("display", "none ");
            }
            else {
                // console.log("abort");
                invalid_response_count++;
            }
        },
        "complete" : function() {

            // 検索ステータスを更新
            response_count++;
            update_search_status();
            currentRequest = null;
        }

    });

}, 200);
