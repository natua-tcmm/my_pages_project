// クリック時選択状態とする
$("#bpm-input").on("click", function () { this.select(); });

// -------------------------------

// ボタンで値を変化させ、計算する
$(".bpm-button").on("click", function () {

    var bpm = Number($("#bpm-input").val());
    bpm += Number($(this).val());
    $("#bpm-input").val(bpm);
    calc();

});

// BPMが変化したときに計算する
$("#bpm-input").change(function () { calc(); });

// 読み込んだときに計算する
$(document).ready(function(){

    // クエリ文字列からbpm入力
    const searchParams = new URLSearchParams(window.location.search)
    if( searchParams.has('bpm') ){
        $("#bpm-input").val(searchParams.get('bpm'))
    }

    calc();
});


// -------------------------------

// いろいろ計算する
function calc() {

    var bpm = Number($("#bpm-input").val());
    if( bpm<0 ){
        $("#bpm-input").val(0);
        bpm=0
    }

    $(".inputvalue-indicate").each(function(){
        $(this).html("入力値: BPM "+bpm);
    });


    // n分音符相互変換
    calc_kosuri(bpm);
    calc_zen(bpm);
    calc_nbu(bpm);
    calc_3600(bpm);

};

// -------------------------------

// 擦り情報
function calc_kosuri(bpm) {

    // AJ・AJC通過可能なn分
    var n_aj  = 1800 / bpm;
    var n_ajc = 3600 / bpm;

    // メイン表示を変える
    // 8分
    if( n_ajc <= 8 ){
        $("#kosuri-8-oo").css("display","inline");
        $("#kosuri-8-o" ).css("display","none");
        $("#kosuri-8-x" ).css("display","none");
        $("#kosuri-8-info").html("理論値通過できます");
    }
    else if( n_aj <= 8 ){
        $("#kosuri-8-oo").css("display","none");
        $("#kosuri-8-o" ).css("display","inline");
        $("#kosuri-8-x" ).css("display","none");
        $("#kosuri-8-info").html("AJ通過できます");
    }
    else{
        $("#kosuri-8-oo").css("display","none");
        $("#kosuri-8-o" ).css("display","none");
        $("#kosuri-8-x" ).css("display","inline");
        $("#kosuri-8-info").html("ATTACKが出ます");
    }

    // 16分
    if( n_ajc <= 16 ){
        $("#kosuri-16-oo").css("display","inline");
        $("#kosuri-16-o" ).css("display","none");
        $("#kosuri-16-x" ).css("display","none");
        $("#kosuri-16-info").html("理論値通過できます");
    }
    else if( n_aj <= 16 ){
        $("#kosuri-16-oo").css("display","none");
        $("#kosuri-16-o" ).css("display","inline");
        $("#kosuri-16-x" ).css("display","none");
        $("#kosuri-16-info").html("AJ通過できます");
    }
    else{
        $("#kosuri-16-oo").css("display","none");
        $("#kosuri-16-o" ).css("display","none");
        $("#kosuri-16-x" ).css("display","inline");
        $("#kosuri-16-info").html("ATTACKが出ます");
    }

    // 24分
    if( n_ajc <= 24 ){
        $("#kosuri-24-oo").css("display","inline");
        $("#kosuri-24-o" ).css("display","none");
        $("#kosuri-24-x" ).css("display","none");
        $("#kosuri-24-info").html("理論値通過できます");
    }
    else if( n_aj <= 24 ){
        $("#kosuri-24-oo").css("display","none");
        $("#kosuri-24-o" ).css("display","inline");
        $("#kosuri-24-x" ).css("display","none");
        $("#kosuri-24-info").html("AJ通過できます");
    }
    else{
        $("#kosuri-24-oo").css("display","none");
        $("#kosuri-24-o" ).css("display","none");
        $("#kosuri-24-x" ).css("display","inline");
        $("#kosuri-24-info").html("ATTACKが出ます");
    }

    // 詳細表示を変える
    $("#kosuri-n-aj").html(n_aj.toFixed(2))
    $("#kosuri-n-ajc").html(n_ajc.toFixed(2))

};

// -------------------------------

// 全押し情報
function calc_zen(bpm) {


    // メイン表示を変える
    // 8分
    if( bpm*8 <= 1440 ){
        $("#zen-8-oo").css("display","inline");
        $("#zen-8-o" ).css("display","none");
        $("#zen-8-x" ).css("display","none");
        $("#zen-8-info").html("全押しできます");
    }
    else if( bpm*8 <= 1800 ){
        $("#zen-8-oo").css("display","none");
        $("#zen-8-o" ).css("display","inline");
        $("#zen-8-x" ).css("display","none");
        $("#zen-8-info").html("全押しできます(遅BREAK注意)");
    }
    else{
        $("#zen-8-oo").css("display","none");
        $("#zen-8-o" ).css("display","none");
        $("#zen-8-x" ).css("display","inline");
        $("#zen-8-info").html("巻き込む可能性があります");
    }

    // 12分
    if( bpm*12 <= 1440 ){
        $("#zen-12-oo").css("display","inline");
        $("#zen-12-o" ).css("display","none");
        $("#zen-12-x" ).css("display","none");
        $("#zen-12-info").html("全押しできます");
    }
    else if( bpm*12 <= 1800 ){
        $("#zen-12-oo").css("display","none");
        $("#zen-12-o" ).css("display","inline");
        $("#zen-12-x" ).css("display","none");
        $("#zen-12-info").html("全押しできます(遅BREAK注意)");
    }
    else{
        $("#zen-12-oo").css("display","none");
        $("#zen-12-o" ).css("display","none");
        $("#zen-12-x" ).css("display","inline");
        $("#zen-12-info").html("巻き込む可能性があります");
    }

    // 16分
    if( bpm*16 <= 1440 ){
        $("#zen-16-oo").css("display","inline");
        $("#zen-16-o" ).css("display","none");
        $("#zen-16-x" ).css("display","none");
        $("#zen-16-info").html("全押しできます");
    }
    else if( bpm*16 <= 1800 ){
        $("#zen-16-oo").css("display","none");
        $("#zen-16-o" ).css("display","inline");
        $("#zen-16-x" ).css("display","none");
        $("#zen-16-info").html("全押しできます(遅BREAK注意)");
    }
    else{
        $("#zen-16-oo").css("display","none");
        $("#zen-16-o" ).css("display","none");
        $("#zen-16-x" ).css("display","inline");
        $("#zen-16-info").html("巻き込む可能性があります");
    }

    // 詳細表示を変える
    var n_oo  = 1440/bpm;
    var n_o = 1800/bpm;

    $("#zen-n-oo").html(n_oo.toFixed(2));
    $("#zen-n-o").html(n_o.toFixed(2));

};

// -------------------------------

// n分音符相互変換
function calc_nbu(bpm) {

    c = 1
    $("#tanni").html("[ms]")
    if ($("#disp_f").prop("checked")){
        c = 60/1000
        $("#tanni").html("[F]")
    }

    $("#kankaku-4").html(  ( 1000*60*c/bpm/   1 ).toFixed(2));
    $("#kankaku-6").html(  ( 1000*60*c/bpm/ 1.5 ).toFixed(2));
    $("#kankaku-8").html(  ( 1000*60*c/bpm/   2 ).toFixed(2));
    $("#kankaku-12").html( ( 1000*60*c/bpm/   3 ).toFixed(2));
    $("#kankaku-16").html( ( 1000*60*c/bpm/   4 ).toFixed(2));
    $("#kankaku-192").html(( 1000*60*c/bpm/   5 ).toFixed(2));
    $("#kankaku-24").html( ( 1000*60*c/bpm/   6 ).toFixed(2));
    $("#kankaku-32").html( ( 1000*60*c/bpm/   8 ).toFixed(2));
    $("#kankaku-48").html( ( 1000*60*c/bpm/  12 ).toFixed(2));
    // $("#kankaku-n").html(  ( 1000*60*c/bpm/   1 ).toFixed(2));

    $("#henkan-4").html(  (    4 * bpm/16 ).toFixed(2));
    $("#henkan-6").html(  (    6 * bpm/16 ).toFixed(2));
    $("#henkan-8").html(  (    8 * bpm/16 ).toFixed(2));
    $("#henkan-12").html( (   12 * bpm/16 ).toFixed(2));
    $("#henkan-16").html( (   16 * bpm/16).toFixed(2));
    $("#henkan-192").html(( 19.2 * bpm/16 ).toFixed(2));
    $("#henkan-24").html( (   24 * bpm/16 ).toFixed(2));
    $("#henkan-32").html( (   32 * bpm/16 ).toFixed(2));
    $("#henkan-48").html( (   48 * bpm/16 ).toFixed(2));
    // $("#henkan-n").html((   1 * bpm/16 ).toFixed(2));

};

// n分相互変換-表示切替
$("#disp_detail").on("click", function () {

    if ($("#disp_detail").prop("checked"))
        $(".nbu-detail").css("display", "table-row");
    else
        $(".nbu-detail").css("display", "none");

});

$("#disp_f").on("click", function () { calc(); });


// -------------------------------

// 族情報
function calc_3600(bpm){

    if( 3600%bpm==0 ){
        $("#jicon-36-o").css("display","inline");
        $("#jicon-36-x").css("display","none");
    }
    else{
        $("#jicon-36-o").css("display","none");
        $("#jicon-36-x").css("display","inline");
    }

    if( 7200%bpm==0 ){
        $("#jicon-72-o").css("display","inline");
        $("#jicon-72-x").css("display","none");
    }
    else{
        $("#jicon-72-o").css("display","none");
        $("#jicon-72-x").css("display","inline");
    }

    // 60fps
    if( 3600%(bpm*    4 /4)==0 ){$("#zure-60-4-o").css("display","inline");$("#zure-60-4-x").css("display","none");}
    else{$("#zure-60-4-o").css("display","none");$("#zure-60-4-x").css("display","inline");}
    if( 3600%(bpm*    6 /4)==0 ){$("#zure-60-6-o").css("display","inline");$("#zure-60-6-x").css("display","none");}
    else{$("#zure-60-6-o").css("display","none");$("#zure-60-6-x").css("display","inline");}
    if( 3600%(bpm*    8 /4)==0 ){$("#zure-60-8-o").css("display","inline");$("#zure-60-8-x").css("display","none");}
    else{$("#zure-60-8-o").css("display","none");$("#zure-60-8-x").css("display","inline");}
    if( 3600%(bpm*   12 /4)==0 ){$("#zure-60-12-o").css("display","inline");$("#zure-60-12-x").css("display","none");}
    else{$("#zure-60-12-o").css("display","none");$("#zure-60-12-x").css("display","inline");}
    if( 3600%(bpm*   16 /4)==0 ){$("#zure-60-16-o").css("display","inline");$("#zure-60-16-x").css("display","none");}
    else{$("#zure-60-16-o").css("display","none");$("#zure-60-16-x").css("display","inline");}
    if( 3600%(bpm* 19.2 /4)==0 ){$("#zure-60-192-o").css("display","inline");$("#zure-60-192-x").css("display","none");}
    else{$("#zure-60-192-o").css("display","none");$("#zure-60-192-x").css("display","inline");}
    if( 3600%(bpm*   24 /4)==0 ){$("#zure-60-24-o").css("display","inline");$("#zure-60-24-x").css("display","none");}
    else{$("#zure-60-24-o").css("display","none");$("#zure-60-24-x").css("display","inline");}
    if( 3600%(bpm*   32 /4)==0 ){$("#zure-60-32-o").css("display","inline");$("#zure-60-32-x").css("display","none");}
    else{$("#zure-60-32-o").css("display","none");$("#zure-60-32-x").css("display","inline");}
    if( 3600%(bpm*   48 /4)==0 ){$("#zure-60-48-o").css("display","inline");$("#zure-60-48-x").css("display","none");}
    else{$("#zure-60-48-o").css("display","none");$("#zure-60-48-x").css("display","inline");}

    // 120fps
    if( 7200%(bpm*    4 /4)==0 ){$("#zure-120-4-o").css("display","inline");$("#zure-120-4-x").css("display","none");}
    else{$("#zure-120-4-o").css("display","none");$("#zure-120-4-x").css("display","inline");}
    if( 7200%(bpm*    6 /4)==0 ){$("#zure-120-6-o").css("display","inline");$("#zure-120-6-x").css("display","none");}
    else{$("#zure-120-6-o").css("display","none");$("#zure-120-6-x").css("display","inline");}
    if( 7200%(bpm*    8 /4)==0 ){$("#zure-120-8-o").css("display","inline");$("#zure-120-8-x").css("display","none");}
    else{$("#zure-120-8-o").css("display","none");$("#zure-120-8-x").css("display","inline");}
    if( 7200%(bpm*   12 /4)==0 ){$("#zure-120-12-o").css("display","inline");$("#zure-120-12-x").css("display","none");}
    else{$("#zure-120-12-o").css("display","none");$("#zure-120-12-x").css("display","inline");}
    if( 7200%(bpm*   16 /4)==0 ){$("#zure-120-16-o").css("display","inline");$("#zure-120-16-x").css("display","none");}
    else{$("#zure-120-16-o").css("display","none");$("#zure-120-16-x").css("display","inline");}
    if( 7200%(bpm* 19.2 /4)==0 ){$("#zure-120-192-o").css("display","inline");$("#zure-120-192-x").css("display","none");}
    else{$("#zure-120-192-o").css("display","none");$("#zure-120-192-x").css("display","inline");}
    if( 7200%(bpm*   24 /4)==0 ){$("#zure-120-24-o").css("display","inline");$("#zure-120-24-x").css("display","none");}
    else{$("#zure-120-24-o").css("display","none");$("#zure-120-24-x").css("display","inline");}
    if( 7200%(bpm*   32 /4)==0 ){$("#zure-120-32-o").css("display","inline");$("#zure-120-32-x").css("display","none");}
    else{$("#zure-120-32-o").css("display","none");$("#zure-120-32-x").css("display","inline");}
    if( 7200%(bpm*   48 /4)==0 ){$("#zure-120-48-o").css("display","inline");$("#zure-120-48-x").css("display","none");}
    else{$("#zure-120-48-o").css("display","none");$("#zure-120-48-x").css("display","inline");}

};
