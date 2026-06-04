import random
from django.db import models
from django.contrib import admin

# ==========================================================
# 🧱 1. 基礎實體：班級與教師模型
# ==========================================================
class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # 🔒 密碼欄位
    gender = models.CharField(max_length=1, default='U')
    specialty = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'school_teachers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SchoolClass(models.Model):
    name = models.CharField(max_length=50)
    grade_level = models.IntegerField(default=1)
    academic_year = models.CharField(max_length=10, default="2026")
    
    homeroom_teacher = models.ForeignKey(
        'Teacher',               
        on_delete=models.SET_NULL, 
        null=True,               
        blank=True,              
        related_name='school_classes' 
    )

    class Meta:
        db_table = 'school_classes'

    def __str__(self):
        return self.name


# ==========================================================
# 📘 2. 核心實體：課程模型
# ==========================================================
class Course(models.Model):
    """Course Specifications Model"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, help_text="Detailed course description")
    credits = models.PositiveIntegerField(default=3)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='courses')

    # 💡 核心新增：星期、時間、教室欄位
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
    ]
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES, default='Mon', verbose_name="上課星期")
    time_slot = models.CharField(max_length=50, default='09:00 - 12:00', verbose_name="上課時間")
    classroom = models.CharField(max_length=50, default='Lecture Hall A', verbose_name="上課教室")

    class Meta:
        db_table = 'school_courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self) -> str:
        return f"Course: {self.name} ({self.code})"
# class Course(models.Model):
#     """Course Specifications Model"""
#     code = models.CharField(max_length=20, unique=True)
#     name = models.CharField(max_length=150)
#     description = models.TextField(blank=True, help_text="Detailed course description")
#     credits = models.PositiveIntegerField(default=3)
#     teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='courses')

#     class Meta:
#         db_table = 'school_courses'
#         verbose_name = 'Course'
#         verbose_name_plural = 'Courses'

#     def __str__(self) -> str:
#         return f"Course: {self.name} ({self.code})"


# ==========================================================
# 🎓 3. 核心實體：學生模型
# ==========================================================

class Student(models.Model):
    """Student Profile Model"""
    student_id = models.CharField(max_length=20, unique=True, help_text="Unique School Student ID")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name="Login Password")

    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, related_name='students')
    enroll_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # 🌟 核心進化：多對多選課，將真實數據委託給 Enrollment 協調表
    courses = models.ManyToManyField(Course, through='Enrollment', related_name='students')

    class Meta:
        db_table = 'school_students'

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.student_id})"


# ==========================================================
# 🌟 4. 終極核心：選課與成績協調表（順序移至上方，防止 Python 報錯）
# ==========================================================
class Enrollment(models.Model):
    """🌟 Student Course Enrollment & Grading Matrix 🌟"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    # 數據完美隔離！分數與出席率真金白銀存在這裡
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    
    class Meta:
        db_table = 'school_enrollments'
        unique_together = ('student', 'course')

    def __str__(self) -> str:
        return f"{self.student.first_name} -> {self.course.name} (Score: {self.score})"


# ==========================================================
# 🌟 5. 行政管理人員模型
# ==========================================================
class Staff(models.Model):
    class TitleChoices(models.TextChoices):
        PRINCIPAL = 'PR', 'Principal'
        DIRECTOR = 'DI', 'Director'
        COORDINATOR = 'CO', 'Coordinator'
        OFFICER = 'OF', 'Administrative Officer'
        CLERK = 'CL', 'Clerk'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=2, choices=TitleChoices.choices, default=TitleChoices.OFFICER)
    department = models.CharField(max_length=100)
    hire_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'school_staff'
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'

    def __str__(self) -> str:
        return f"Staff: {self.first_name} {self.last_name} ({self.get_title_display()})"


# ==========================================================
# ⚙️ 6. Django Admin 後台配置區
# ==========================================================
admin.site.register(Teacher)
admin.site.register(Staff)
admin.site.register(Course)

# 🟢 建立選課內嵌介面：讓管理員可以直接在學生的編輯頁面改分數、看選課
class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    fields = ['course', 'score', 'attendance_rate']  
    extra = 1  

# 🟢 學生管理介面：掛載上面的內嵌成績單
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_id', 'first_name', 'last_name', 'school_class', 'is_active']
    inlines = [EnrollmentInline]  # 🌟 直接在學生身上看見所有功課分數！

# 🟢 班級管理介面
@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'grade_level', 'academic_year', 'homeroom_teacher']

# 🟢 獨立註冊 Enrollment，讓你可以有一個總表檢視全校所有分數
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'course', 'score', 'attendance_rate']