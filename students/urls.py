from django.urls import path
from . import views

# 🌟 100% 對齊總路由的 namespace='students'，確保學生端反向解析絕不卡死轉圈圈
app_name = 'students'

urlpatterns = [
    # 學生端首頁 (Student Hub)
    path('', views.student_index, name='index'),
    
    # 3 個學生端核心功能網頁路由（課表、成績查詢、線上選課）
    path('timetable/', views.timetable_view, name='timetable'),
    path('report/', views.grades_report_view, name='grades_report'),
    path('enroll/', views.enroll_view, name='enroll'),
    # 在你的 student/urls.py 的 urlpatterns 內加上這一行：
    path('profile/', views.student_profile_view, name='profile'),
]
