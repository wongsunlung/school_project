from django.urls import path
from . import views

# 🌟 100% 對齊總路由的 namespace='office'，讓 Django 找得到 pattern name
app_name = 'office'

urlpatterns = [
    # 行政端 Dashboard 首頁
    path('', views.office_index, name='index'),
    
    # 4 個行政管理英文網頁路由（精準對齊您實體的網頁變數名）
    path('classroom/', views.admin_classroom, name='admin_classroom'),
    path('courses/', views.admin_courses, name='admin_courses'),
    path('students/', views.admin_students, name='admin_students'),
    path('teachers/', views.admin_teachers, name='admin_teachers'),
]
