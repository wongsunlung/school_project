from django.urls import path
from . import views

# 🌟 100% 對齊總路由的 namespace='teachers'，確保教師端反向解析絕不卡死
app_name = 'teachers'

urlpatterns = [
    # 教師端 Portal 首頁
    path('', views.teacher_index, name='index'),
    
    # 教師端 2 大核心功能網頁路由（出勤紀錄、成績輸入）
    path('attendance/', views.attendance_list, name='attendance'),
    path('grades/', views.grades_list, name='grades'),
]
