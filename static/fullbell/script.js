
// inputをclickで選択状態にする
$("#get_bell_count").on("click", function () { this.select(); });
$("#all_bell_count").on("click", function () { this.select(); });
$("#technical_score").on("click", function () { this.select(); });


// エラーを表示する関数
var disp_error = function (message) {
    $("#alert-error").css("display", "flex");
    $("#error_message").html(message);
};

// 有効性確認の関数
var valid_check = function (input) {

    // 正規表現パターン 0以上の自然数
    var pattern = /^\d*$/;

    if (input.length == 0) {
        disp_error("未入力の欄があります");
        return false;
    }

    if (!pattern.test(input)) {
        disp_error("不正な値が入力されている欄があります");
        return false;
    }

    return true;

};

// 小数点第p位で切り捨て
var kirisute = function (num, p) {
    return Math.floor(num * Math.pow(10, p)) / Math.pow(10, p);
};

// 負の値で達成表示
var score_tassei = function (score, target) {
    if (target > score) return (target - score).toString();
    else return "達成!";
};

var original_score_for_tweet = -1;
var result_score_for_tweet = -1;

// ボタンが押されたら実行される関数
$("#calc_button").on("click", function () {

    var get_bell_count = $("#get_bell_count").val();
    var all_bell_count = $("#all_bell_count").val();
    var technical_score = $("#technical_score").val();
    original_score_for_tweet = technical_score

    // エラーを非表示に
    $("#alert-error").css("display", "none");

    // 有効性確認
    if (!(valid_check(get_bell_count) && valid_check(all_bell_count) && valid_check(technical_score))) {
        disp_error("入力した値を確認してください(未入力/入力値が不正)");
        return;
    }

    // 数値に変換
    get_bell_count = Number(get_bell_count);
    all_bell_count = Number(all_bell_count);
    technical_score = Number(technical_score);

    // 計算
    var bell_score = 60000 * (get_bell_count / all_bell_count);
    var notes_score = technical_score - bell_score;
    var result_score = Math.floor(notes_score + 60000);
    result_score_for_tweet = result_score

    // エラーチェック
    if (get_bell_count > all_bell_count) {
        disp_error("入力した値を確認してください(ベル数が不正)");
        return;
    }
    if (result_score > 1010000) {
        disp_error("入力した値を確認してください(結果が理論値超え)");
        return;
    }

    // 結果表示
    $("#result-hi").html(Math.floor(result_score / 10000));
    $("#result-lo").html((result_score % 10000).toString().padStart(4, "0"));

    $("#to_sss").html("SSSまで : " + score_tassei(technical_score, 1000000) + " → " + score_tassei(result_score, 1000000));
    $("#to_sssp").html("SSS+まで : " + score_tassei(technical_score, 1007500) + " → " + score_tassei(result_score, 1007500));

    $("#score_minus_bell").html("ベルによる合計失点 : " + kirisute(60000 - bell_score, 1));
    $("#score_one_bell").html("ベル1つあたりの配点 : " + kirisute(60000 / all_bell_count, 1));

    $("#score_bell").html("ベルによるスコア : " + kirisute(bell_score, 1) + " / 60000 ( MAX-" + kirisute(60000 - bell_score, 1) + " | " + kirisute(bell_score / 600.00, 2) + "%)");
    $("#score_notes").html("ノーツによるスコア : " + kirisute(notes_score, 1) + " / 950000 ( MAX-" + kirisute(950000 - notes_score, 1) + " | " + kirisute(notes_score / 9500.00, 2) + "%)");

    $("#tweet").prop("disabled", false);
    $("#tweet-copy").prop("disabled", false);

    return;

});

// 懺悔ツイート
$("#tweet").on("click", function () {

    // ツイート生成
    var base_url = "https://twitter.com/intent/tweet";
    var text = "はい、私は本来" + result_score_for_tweet + "点だったスコアを、ベルを取り逃した結果" + original_score_for_tweet + "点にしてしまい…";
    // var hashtags = "";

    // リンクを開く
    var tweetLink = base_url + "?text=" + encodeURIComponent(text);
    // var tweetLink = base_url + "?text=" + encodeURIComponent(text) + "&hashtags=" + hashtags;
    window.open(tweetLink);

});
// 懺悔コピペ
$("#tweet-copy").on("click", function () {

    var text = "はい、私は本来" + result_score_for_tweet + "点だったスコアを、ベルを取り逃した結果" +original_score_for_tweet + "点にしてしまい…";

    // コピー
    if( !navigator.clipboard ) {
        alert("エラー:コピーできませんでした。ブラウザが対応していない可能性があります。");
    }
    else{
        navigator.clipboard.writeText(text).then(
            () => {
                alert("コピーしました。")
            },
            () => {
                alert("コピーに失敗しました。")
            });
    }
});
