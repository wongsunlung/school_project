from django.contrib import admin
from .models import Teacher, Staff, Course, SchoolClass, Student, Score

# 將 5 大核心模型加上學生實體，老老實實註冊進管理後台
admin.site.register(Teacher)
admin.site.register(Staff)
admin.site.register(Course)
admin.site.register(SchoolClass)
admin.site.register(Student)
admin.site.register(Score)
