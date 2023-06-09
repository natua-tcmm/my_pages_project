// 課題曲の数
var kadaikyoku_count = 3;

// ---------------------------------

// ルーレット表示
function roulette(n, all) {

    var times = [0];
    for (let i = 0; i < all * 7 + n - 1; i++) {
        times.push(times[times.length - 1] + 50)
    }
    for (let i = 0; i < all * 5; i++) {
        times.push(times[times.length - 1] + 75)
    }
    for (let i = 0; i < all * 4; i++) {
        times.push(times[times.length - 1] + 100)
    }
    for (let i = 0; i < all * 2; i++) {
        times.push(times[times.length - 1] + 150)
    }

    for (let i = 0; i < times.length; i++) {
        setTimeout(function () { roulette_onoff(i % all) }, times[i]);
    }

    return times[times.length - 1];

}

// ルーレット表示(単位)
function roulette_onoff(index_on) {

    for (var k = 1; k <= 3; k++) {

        if (k == index_on + 1) {
            $("#kadai-check-" + k).attr('checked', true).prop("checked", true).change();
            // $("#kadai-in-" + k).addClass("is-valid").change();
        }
        else {
            $("#kadai-check-" + k).attr('checked', false).prop("checked", false).change();
            $("#kadai-in-" + k).removeClass("is-valid").change();
        }

    }

}

// ---------------------------------

// 機種名が選ばれたら試合情報を読み込む
$("#kisyu-select").on("change", function (e) {
    load_kadaikyoku(e);
});

var load_kadaikyoku = function (e) {

    $("#loading-text").css("display", "");

    // 通常の送信処理を止める
    e.preventDefault();

    // 送信する
    $.ajax({
        'url': send_url,
        'type': 'POST',
        'data': {
            "csrfmiddlewaretoken": csrfmiddlewaretoken,
            "kisyu": $("#kisyu-select").val(),
            "game": "",
        },
        'dataType': 'json',
    })
        //成功時
        .done(function (response) {

            $("#loading-text").css("display", "none");

            // 機種名から試合名
            if (response.games_response) {
                // 今表示されてるやつを消す
                $(".games").remove();
                // 新しく表示する
                for (var i = 0; i < response.games_response.length; i++) {
                    $("#game-select").prepend(response.games_response[i]);
                }
                $("#game-select").prepend('<option class="games" selected>(試合を選択…)</option>');
            }
            else {
                $(".games").remove();
                $("#game-select").prepend('<option class="games" selected>(まずは機種を選んでください)</option>');
            }

        })
        //失敗時
        .fail(function () {
            alert("ajax送信に失敗しました。");
            $("#loading-text").css("display", "none");
            // 今表示されてるやつを消す
            $(".games").remove();
        });
}

// 機種名と試合から試合情報を自動入力する
$("#auto-input").on("click", function (e) {

    auto_input_kadaikyoku(e);

});

var auto_input_kadaikyoku = function (e) {

    $("#loading-text").css("display", "");

    // 通常の送信処理を止める
    e.preventDefault();

    // 送信する
    $.ajax({
        'url': send_url,
        'type': 'POST',
        'data': {
            "csrfmiddlewaretoken": csrfmiddlewaretoken,
            "kisyu": $("#kisyu-select").val(),
            "game": $("#game-select").val(),
        },
        'dataType': 'json',
    })
        //成功時
        .done(function (response) {

            $("#loading-text").css("display", "none");

            // 試合情報の自動入力
            if (response.games_info) {

                var r = response.games_info;

                reset_form();

                $("#vs-game").val(r.vs_game);
                $("#vs-name").val(r.vs_name);
                $("#vs-player").val(r.vs_player);

                kadaikyoku_count = r.kadai_count;

                for (var i = 0; i < r.kadai.length; i++) {
                    $("#kadai-in-" + (i + 1)).val(r.kadai[i]);
                }

                if (kadaikyoku_count == 1) {
                    $("#kadai-check-1").attr('checked', true).prop("checked", true).change()
                }

            }
            else {

            }
        })
        //失敗時
        .fail(function () {
            alert("ajax送信に失敗しました。");
            $("#loading-text").css("display", "none");
        });
}

// ---------------------------------

// 抽選処理
$("#start").on("click", function () {

    // 抽選ボタンをdisableに
    $("#start").prop("disabled", true);

    var all = 3;
    if ($("#kadai-in-3").val() == "")
        var all = 2;

    // 抽選
    var min = 1; var max = all;
    var n = Math.floor(Math.random() * (max + 1 - min)) + min;

    // ルーレットを回す演出
    roulette_onoff(-10);
    var t = roulette(n, all);
    console.log("抽選結果: "+n,"抽選時間: "+t+"ms");

    // ルーレット停止後の処理
    setTimeout(function () {

        $("#kadai-in-" + n).addClass("is-valid");
        $("#start").prop("disabled", false);
        $("#tweet").prop("disabled", false);

    }, t);

});

// ツイート
$("#tweet").on("click", function () {

    // 情報取得
    var vs_game = $("#vs-game").val();
    var vs_name = $("#vs-name").val();
    var vs_player = $("#vs-player").val();
    var hashtags = $("#hashtag-in").val();

    var c = false;

    for (var j = 1; j <= 3; j++) {

        if ($("#kadai-check-" + j).prop("checked")) {
            var kadai_song = $("#kadai-in-" + j).val();
            c = true;
            break;
        }

    }

    if (c == false && kadaikyoku_count > 0) {
        alert("ツイート前に、抽選を行うか手動選択してください。");
    }
    else {
        // ツイート生成
        var base_url = "https://twitter.com/intent/tweet";
        var text = vs_game + "部門" + vs_name + "、" + vs_player + "の対決！";
        if (kadaikyoku_count > 0) {
            text += "\n課題曲は『" + kadai_song + "』です！";
        }

        // リンクを開く
        var tweetLink = base_url + "?text=" + encodeURIComponent(text) + "&hashtags=" + hashtags;
        window.open(tweetLink);
    }


});

// リセット
$("#reset").on("click", function () {

    reset_form();

});

var reset_form = function () {

    $("#vs-game").val("");
    $("#vs-name").val("");
    $("#vs-player").val("");

    for (var i = 0; i < 3; i++) {
        $("#kadai-in-" + (i + 1)).val("");
        $("#kadai-check-" + (i + 1)).attr('checked', false).prop("checked", false).change();
        $("#kadai-in-" + (i + 1)).removeClass("is-valid").change();
    }

};
