from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. 內建超級管理員後台
    path('admin/', admin.site.urls),

    # 2. 🌟 對齊老師 pages 精髓：main_base 負責全站大首頁 (第一路徑 '')
    path('', include('main_base.urls', namespace='main_base')),

    # 3. 用戶驗證與註冊模組
    path('users/', include('users.urls', namespace='users')),

    # 4. 行政管理端模組
    path('office/', include('office.urls', namespace='office')),

    # 5. 教師教學端模組
    path('teachers/', include('teachers.urls', namespace='teachers')),

    # 6. 學生事務端模組
    path('students/', include('students.urls', namespace='students')),
]
