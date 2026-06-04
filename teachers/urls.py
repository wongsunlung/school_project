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

    # ==========================================================
    # 💾 實時儲存 API 路由補給線：供前端 JavaScript 非同步發送資料
    # ==========================================================
    path('api/update-attendance/', views.api_update_attendance, name='api_update_attendance'),
    path('api/update-score/', views.api_update_score, name='api_update_score'),
    path('profile/', views.teacher_profile_view, name='profile'), # 填入對應的 name='profile'
]
