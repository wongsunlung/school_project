# from django.contrib import admin
# from .models import Score

# # 🟢 徹底退讓：把所有基礎註冊都拿掉，避免與其他檔案撞車！
# # 🟢 只保留這段單獨的特製版 Score 註冊
# try:
#     @admin.register(Score)
#     class ScoreAdmin(admin.ModelAdmin):
#         list_display = ['id']
# except admin.sites.AlreadyRegistered:
#     pass
# from django.contrib import admin
# from .models import Student

# # 先安全取消舊的註冊，防止重複註冊引發死機
# try:
#     admin.site.unregister(Student)
# except admin.sites.NotRegistered:
#     pass

# @admin.register(Student)
# class StudentAdmin(admin.ModelAdmin):
#     # 這裡放你想在列表看到的欄位，最後一個就是我們自訂的 'get_courses'
#     list_display = ('student_id', 'first_name', 'last_name', 'email', 'school_class', 'get_courses')
    
#     # 這是專門用來安全讀取多對多課程的函數
#     def get_courses(self, obj):
#         # 這裡的 .courses 完全對齊你 models.py 裡的定義
#         # return ", ".join([course.name for course in obj.courses.all()])
#         return ", ".join([str(course) for course in obj.courses.all()])
    
#     # 將後台顯示的欄位名稱定義為「課程」
#     get_courses.short_description = '課程'
# # 📥 請直接複製以下整段，去代替你原本的 class StudentAdmin 程式碼

#這是新的代碼
# admin.py
from django.contrib import admin
# 💡 重點 1：確保你導入了 Enrollment 模型
from .models import Student, Enrollment 

# 先安全取消舊的註冊，防止重複註冊引發死機
try:
    admin.site.unregister(Student)
except admin.sites.NotRegistered:
    pass

# 💡 重點 2：建立一個 Inline 類別
class EnrollmentInline(admin.TabularInline):  
    model = Enrollment
    extra = 1  # 預設顯示幾個空白列讓你快速幫學生新增課程
    # 如果不想在內嵌表單看到某些特定欄位，可以用 exclude = ('欄位名',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'email', 'school_class', 'get_courses')
    
    # 💡 重點 3：把剛剛建立的 Inline 加入 StudentAdmin
    inlines = [EnrollmentInline]
    
    # 這是專門用來安全讀取多對多課程的函數（列表頁顯示用）
    def get_courses(self, obj):
        return ", ".join([str(course) for course in obj.courses.all()])
    
    # 將後台顯示的欄位名稱定義為「課程」
    get_courses.short_description = 'courses'


