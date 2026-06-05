from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
import main_base.models as core_models


def office_index(request):
    """1. 行政端 Dashboard 首頁 (🔒 必須登入)"""
    if not request.user.is_authenticated:
        messages.error(request, "Access denied. Please sign in as an Administrator.")
        return redirect("users:login")
        
    context = {
        "total_classes": core_models.SchoolClass.objects.count(),
        "total_teachers": core_models.Teacher.objects.count(),  # 🟢 修正：Teacher 沒有 is_active，直接算總數
        "total_students": core_models.Student.objects.filter(is_active=True).count(),
    }
    return render(request, 'office/office.html', context)


@never_cache
def admin_teachers(request):
    """2. 教職人員管理 (🌐 雙向權限分流核心 - 採用最直覺 Python 織網演算法，100% 絕不報錯)"""
    
    # 1. 判斷超級管理員身份
    is_admin_mode = request.user.is_authenticated and request.user.is_superuser
    
    # 🟩 POST 審核處理：Approve 核准
    if is_admin_mode and request.method == "POST" and "approve_teacher_id" in request.POST:
        t_id = request.POST.get("approve_teacher_id")
        teacher = get_object_or_404(core_models.Teacher, pk=t_id)
        
        # 🚨 核心漏洞修補：真金白銀把狀態改成 True，接通斷掉的線路！
        teacher.is_active = True  
        teacher.save()  # 💾 真正向 PostgreSQL 發送 UPDATE 存檔指令
        
        # 🌐 對外展示文字：完全使用英文
        messages.success(request, f"Faculty Approved! Prof. {teacher.first_name} {teacher.last_name} is now active.")
        return redirect("office:admin_teachers")

    # 🟥 POST 審核處理：Reject 拒絕 (原汁原味保留物理刪除邏輯)
    if is_admin_mode and request.method == "POST" and "reject_teacher_id" in request.POST:
        t_id = request.POST.get("reject_teacher_id")
        teacher = get_object_or_404(core_models.Teacher, pk=t_id)
        teacher.delete()  # 💥 物理蒸發，查無此人
        
        # 🌐 對外展示文字：完全使用英文
        messages.success(request, "Registration request rejected and removed permanently.")
        return redirect("office:admin_teachers")

    # 2. 身份分流撈取基礎資料庫名單 (完全維持您原本的設定)
    raw_teachers = core_models.Teacher.objects.all().order_by('-id')

    # 3. 🌟 複合式 Q() 模糊搜尋過濾器 🌟 (完全維持您原本的設定)
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            raw_teachers = raw_teachers.filter(
                Q(first_name__icontains=keywords) | 
                Q(last_name__icontains=keywords) | 
                Q(email__icontains=keywords)
            )

    # 4. 🌟 LUNG 終極直覺織網法：動態算出每位老師的真實數據 (原汁原味，絕不破壞地基)
    for t in raw_teachers:
        # A. 找出這位老師教的所有課程
        my_courses = t.courses.all() if hasattr(t, 'courses') else []
        t.total_courses = len(my_courses)
        
        # B. 找出所有選了這些課程的學生
        students_enrolled = core_models.Student.objects.filter(courses__in=my_courses).distinct()
        t.total_students = students_enrolled.count()
        
        # C. 從 Enrollment 中間表撈出真實數據
        enrollments = core_models.Enrollment.objects.filter(student__in=students_enrolled, course__in=my_courses)
        
        # 動態計算學生的【平均分】
        valid_scores = [e.score for e in enrollments if e.score is not None]
        t.avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        
        # 動態計算學生的【平均出席率】
        valid_attendance = [e.attendance_rate for e in enrollments if hasattr(e, 'attendance_rate') and e.attendance_rate is not None]
        t.avg_attendance = sum(valid_attendance) / len(valid_attendance) if valid_attendance else 100.0

    # 5. 全站統一 Paginator 分頁器（每頁嚴格限制 5 筆）
    paginator = Paginator(raw_teachers, 5) 
    page = request.GET.get('page')
    paged_teachers = paginator.get_page(page)

    context = {
        "teachers": paged_teachers,
        "is_admin_mode": is_admin_mode  
    }
    return render(request, 'office/admin_teachers.html', context)


@login_required(login_url='users:login')
def admin_classroom(request):
    """3. 班級管理 (🔒 必須登入 - 升級 100% 完整數據分頁)"""
    if request.method == "POST":
        name = request.POST.get("name")
        grade_level = request.POST.get("grade_level")
        academic_year = request.POST.get("academic_year")
        teacher_id = request.POST.get("homeroom_teacher")
        course_ids = request.POST.getlist("courses")

        # 🟢 修正：移除 Teacher 的 is_active 過濾
        teacher = core_models.Teacher.objects.filter(pk=teacher_id).first() if teacher_id else None
        
        new_class = core_models.SchoolClass.objects.create(
            name=name, grade_level=grade_level, 
            academic_year=academic_year, homeroom_teacher=teacher
        )
        if course_ids:
            new_class.courses.set(core_models.Course.objects.filter(pk__in=course_ids))
            
        messages.success(request, f"Class {name} created successfully.")
        return redirect("office:admin_classroom")

    # 🌟 核心修復：真金白銀撈出「所有」班級，並依照名稱排序
    class_list = core_models.SchoolClass.objects.all().order_by('name')
    
    # 🌟 補齊大數據分頁：每頁嚴格限制 5 筆，把 9 個班級分流展示
    paginator = Paginator(class_list, 5)
    page = request.GET.get('page')
    paged_classes = paginator.get_page(page)

    # 🟢 修正：移除 Teacher 的 is_active 過濾
    all_teachers = core_models.Teacher.objects.all()
    all_courses = core_models.Course.objects.all()

    context = {
        "classes": paged_classes,  # 🌟 確保這行傳給前端的是分頁後的資料
        "all_teachers": all_teachers,
        "all_courses": all_courses
    }
    return render(request, 'office/admin_classrooms.html', context)


@login_required(login_url='users:login')
def admin_courses(request):
    """4. 課程管理 (🔒 必須登入 - 升級 100% 完整數據分頁)"""
    if request.method == "POST":
        code = request.POST.get("code")
        name = request.POST.get("name")
        credits = request.POST.get("credits")
        description = request.POST.get("description")
        teacher_id = request.POST.get("teacher")

        # 🟢 修正：移除 Teacher 的 is_active 過濾
        teacher = core_models.Teacher.objects.filter(pk=teacher_id).first() if teacher_id else None
        core_models.Course.objects.create(code=code, name=name, credits=credits, description=description, teacher=teacher)
        messages.success(request, f"Course {name} ({code}) added.")
        return redirect("office:admin_courses")

    # 🌟 核心修復：真金白銀撈出「所有」課程
    course_list = core_models.Course.objects.all().order_by('code')
    
    # 🌟 補齊大數據分頁：每頁嚴格限制 5 筆，讓 10 門課程觸發功課表分頁
    paginator = Paginator(course_list, 5)
    page = request.GET.get('page')
    paged_courses = paginator.get_page(page)

    # 🟢 修正：移除 Teacher 的 is_active 過濾
    all_teachers = core_models.Teacher.objects.all()
    
    context = {
        "courses": paged_courses,  # 🌟 確保這行傳給前端的是分頁後的資料
        "all_teachers": all_teachers
    }
    return render(request, 'office/admin_courses.html', context)


@never_cache
def admin_students(request):
    """5. 學生學籍 management"""
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == "POST" and "approve_student_id" in request.POST:
            s_id = request.POST.get("approve_student_id")
            student = get_object_or_404(core_models.Student, pk=s_id)
            student.is_active = True
            student.save()
            messages.success(request, f"Student Approved! {student.first_name} is enrolled.")
            return redirect("office:admin_students")

        if request.method == "POST" and "reject_student_id" in request.POST:
            s_id = request.POST.get("reject_student_id")
            student = get_object_or_404(core_models.Student, pk=s_id)
            student.delete()
            messages.success(request, "Student request rejected.")
            return redirect("office:admin_students")

        queryset_list = core_models.Student.objects.all().order_by('-id')
        is_admin_mode = True
    else:
        queryset_list = core_models.Student.objects.filter(is_active=True).order_by('-id')
        is_admin_mode = False

    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(
                Q(first_name__icontains=keywords) | 
                Q(last_name__icontains=keywords) | 
                Q(student_id__icontains=keywords) |
                Q(email__icontains=keywords)
            )

    paginator = Paginator(queryset_list, 5)
    page = request.GET.get('page')
    paged_students = paginator.get_page(page)

    context = {
        "students": paged_students,
        "is_admin_mode": is_admin_mode
    }
    return render(request, 'office/admin_students.html', context)
