from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


# 🌟 100% 對齊老師的命名空間金鑰，確保反向解析與跳轉絕對不卡死轉圈圈
app_name = 'users'

urlpatterns = [
    # 登入分流功能路由
    path('login/', views.login_view, name='login'),
    
    # 🌟 滿足您交辦的新需求：新生與新聘老師登記進入系統的註冊路由
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='office:admin_teachers'), name='logout'),

]
