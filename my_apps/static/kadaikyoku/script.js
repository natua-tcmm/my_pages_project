// ルーレット表示
function roulette(n) {

    var times = [0];
    for (let i = 0; i < 21 + n - 1; i++) {
        times.push(times[times.length - 1] + 50)
    }
    for (let i = 0; i < 15; i++) {
        times.push(times[times.length - 1] + 75)
    }
    for (let i = 0; i < 12; i++) {
        times.push(times[times.length - 1] + 100)
    }
    for (let i = 0; i < 6; i++) {
        times.push(times[times.length - 1] + 150)
    }

    for (let i = 0; i < times.length; i++) {
        setTimeout(function () { roulette_onoff(i % 3) }, times[i]);
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

// 自動入力
$("#auto-input").on("click", function () {

    $("#vs-game").val("音ゲー")
    $("#vs-name").val("第1試合")
    $("#vs-player").val("あるふぁさん vs べーたさん")
    $("#kadai-in-1").val("楽曲A")
    $("#kadai-in-2").val("楽曲B")
    $("#kadai-in-3").val("楽曲C")

});

// 抽選処理
$("#start").on("click", function () {

    // 抽選ボタンをdisableに
    $("#start").prop("disabled", true);

    // 抽選
    var min = 1; var max = 3;
    var n = Math.floor(Math.random() * (max + 1 - min)) + min;

    // ルーレットを回す演出
    roulette_onoff(-10);
    var t = roulette(n);
    console.log(n, t);

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

    for (var j = 1; j <= 3; j++) {

        if ($("#kadai-check-" + j).prop("checked")) {
            var kadai_song = $("#kadai-in-" + j).val();
            break;
        }

    }

    // ツイート生成
    var base_url = "https://twitter.com/intent/tweet";
    var text = vs_game + "部門" + vs_name +  "、" + vs_player + "の対決！\n課題曲は『" + kadai_song + "』です！";

    // リンクを開く
    var tweetLink = base_url + "?text=" + encodeURIComponent(text) + "&hashtags=" + hashtags;
    window.open(tweetLink);

});
