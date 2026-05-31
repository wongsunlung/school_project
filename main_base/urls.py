from django.urls import path
from . import views

# 🌟 100% 複製老師 Demo 的命名空間註冊金鑰（確保反向解析絕不卡死轉圈圈）
app_name = 'main_base'

urlpatterns = [
    # 專職負責全站大首頁的調度
    path('', views.index, name='index'),
]
