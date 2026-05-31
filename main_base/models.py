from django.db import models


class Teacher(models.Model):
    """教師模型"""
    
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
    email: str = models.EmailField(unique=True)
    gender: str = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.OTHER
    )
    specialty: str = models.TextField(blank=True, help_text="Teacher's professional specialty introduction")
    hire_date = models.DateField(auto_now_add=True)
    is_active: bool = models.BooleanField(default=True)

    class Meta:
        db_table = 'school_teachers'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self) -> str:
        return f"Teacher: {self.first_name} {self.last_name}"


class Staff(models.Model):
    """行政管理人員模型"""
    
    class TitleChoices(models.TextChoices):
        PRINCIPAL = 'PR', 'Principal'
        DIRECTOR = 'DI', 'Director'
        COORDINATOR = 'CO', 'Coordinator'
        OFFICER = 'OF', 'Administrative Officer'
        CLERK = 'CL', 'Clerk'

    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
    email: str = models.EmailField(unique=True)
    title: str = models.CharField(
        max_length=2,
        choices=TitleChoices.choices,
        default=TitleChoices.OFFICER
    )
    department: str = models.CharField(max_length=100)
    hire_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'school_staff'
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'

    def __str__(self) -> str:
        return f"Staff: {self.first_name} {self.last_name} ({self.get_title_display()})"


class Course(models.Model):
    """課程模型"""
    
    code: str = models.CharField(max_length=20, unique=True)
    name: str = models.CharField(max_length=150)
    description: str = models.TextField(blank=True, help_text="Detailed course description")
    credits: int = models.PositiveIntegerField(default=3)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='courses')

    class Meta:
        db_table = 'school_courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self) -> str:
        return f"Course: {self.name} ({self.code})"


# class SchoolClass(models.Model):
#     """班級模型（避開 Python 關鍵字 class）"""
    
#     name: str = models.CharField(max_length=50, unique=True)
#     grade_level: int = models.PositiveIntegerField()
#     academic_year: str = models.CharField(max_length=9, help_text="Format: 2025-2026")
#     # homeroom_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='homeroom_classes')
#         # 🌟 就在這裡：加上 blank=True，後台就不會再強迫您一定要選擇導師了！
#     homeroom_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, **blank=True**, related_name='homeroom_classes')

#     courses = models.ManyToManyField(Course, related_name='classes', blank=True)

#     class Meta:
#         db_table = 'school_classes'
#         verbose_name = 'Class'
#         verbose_name_plural = 'Classes'

#     def __str__(self) -> str:
#         return f"Class: {self.name}"
class SchoolClass(models.Model):
    """班級模型（避開 Python 關鍵字 class）"""
    
    name: str = models.CharField(max_length=50, unique=True)
    grade_level: int = models.PositiveIntegerField()
    academic_year: str = models.CharField(max_length=9, help_text="Format: 2025-2026")
    # 🌟 核心修正：正式加入 blank=True，讓導師欄位在後台允許保持空白儲存
    homeroom_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='homeroom_classes')
    courses = models.ManyToManyField(Course, related_name='classes', blank=True)

    class Meta:
        db_table = 'school_classes'
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'

    def __str__(self) -> str:
        return f"Class: {self.name}"



class Student(models.Model):
    """學生模型（🌟 正式補全核心實體）"""
    
    student_id: str = models.CharField(max_length=20, unique=True, help_text="Unique School Student ID")
    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
    email: str = models.EmailField(unique=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, related_name='students')
    enroll_date = models.DateField(auto_now_add=True)
    is_active: bool = models.BooleanField(default=True)

        # 🌟 補強大專選課與成績地基（加上 null=True，舊資料絕對不會壞掉報錯！）
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)


    class Meta:
        db_table = 'school_students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


    def __str__(self) -> str:
        return f"Student: {self.first_name} {self.last_name} ({self.student_id})"


class Score(models.Model):
    """成績模型"""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='scores')
    exam_grade = models.DecimalField(max_digits=5, decimal_places=2, help_text="Exam score (0.00 - 100.00)")
    date_recorded = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'school_scores'
        verbose_name = 'Score'
        verbose_name_plural = 'Scores'
        unique_together = ('student', 'course')  # 限制同一名學生在同一門課只能有一筆成績紀錄

    def __str__(self) -> str:
        return f"{self.student.student_id} - {self.course.name}: {self.exam_grade}"
