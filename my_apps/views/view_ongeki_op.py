from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import os,json,datetime,jaconv,re,unicodedata
from django.conf import settings

# --------------------------------------------------

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# オンゲキOP
def ongeki_op(request):

    context = { "title":f"オンゲキ版OVERPOWER {title_base}" ,"is_beta":True, "is_app":True }

    # Ajax処理
    if request.method=="POST":

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        osl_id = post.get("osl_id")







        result = f"にゃーん {osl_id}"




        # お返しする
        response = { "result":result }
        return JsonResponse(response)

    return render(request, 'ongeki_op/ongeki_op.html',context=context)
