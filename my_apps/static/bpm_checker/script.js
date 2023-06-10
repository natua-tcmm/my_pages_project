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
window.onload = function(){

    // クエリ文字列からbpm入力
    const searchParams = new URLSearchParams(window.location.search)
    if( searchParams.has('bpm') ){
        $("#bpm-input").val(searchParams.get('bpm'))
    }

    calc();
};



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
    // $("#henkan-in").html("入力値: BPM "+bpm);
    calc_nbu(bpm);
    calc_3600(bpm);

};

// -------------------------------

// n分音符相互変換
function calc_nbu(bpm) {

    $("#kankaku-4").html(  ( 1000*60/bpm/   1 ).toFixed(2));
    $("#kankaku-6").html(  ( 1000*60/bpm/ 1.5 ).toFixed(2));
    $("#kankaku-8").html(  ( 1000*60/bpm/   2 ).toFixed(2));
    $("#kankaku-12").html( ( 1000*60/bpm/   3 ).toFixed(2));
    $("#kankaku-16").html( ( 1000*60/bpm/   4 ).toFixed(2));
    $("#kankaku-192").html(( 1000*60/bpm/   5 ).toFixed(2));
    $("#kankaku-24").html( ( 1000*60/bpm/   6 ).toFixed(2));
    $("#kankaku-32").html( ( 1000*60/bpm/   8 ).toFixed(2));
    $("#kankaku-48").html( ( 1000*60/bpm/  12 ).toFixed(2));
    // $("#kankaku-n").html(  ( 1000*60/bpm/   1 ).toFixed(2));

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

    if ($("#disp_detail").prop("checked") == true)
        $(".nbu-detail").css("display", "table-row");
    else
        $(".nbu-detail").css("display", "none");

});

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
