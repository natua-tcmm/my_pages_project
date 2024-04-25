from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import requests,re,math,datetime
from bs4 import BeautifulSoup
from django.conf import settings

from .view_ongeki_op import get_ongeki_score_log_player_data

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# テンプレート こいつをコピペして作ろう
def ongeki_rating_all(request):
    context = { "title":f"オンゲキレーティング計算(新曲枠なし) {title_base}" ,"is_beta":True, "is_app":True }
    return render(request, 'ongeki_rating_all/ongeki_rating_all.html',context=context)

def ongeki_rating_act2(request):
    context = { "title":f"オンゲキ brightMEMORY Act.2基準レーティング {title_base}" ,"is_beta":True, "is_app":True }
    return render(request, 'ongeki_rating_act2/ongeki_rating_act2.html',context=context)
