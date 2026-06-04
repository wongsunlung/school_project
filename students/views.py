from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# 🟢 引入主地基多對多核心模型
from main_base.models import Student, Enrollment, Course

# ==========================================================
# 🛠️ 內部防呆機制：確保登入者一定是學生，否則自動抓第一筆進行測試
# ==========================================================
def _get_current_student_or_fallback(request):
    """內部輔助函式：獲取當前學生，若無則抓取第一筆作為測試 fallback"""
    student = Student.objects.filter(email=request.user.email).first()
    if not student:
        student = Student.objects.first()
    return student


# ==========================================================
# 🎓 1. 學生端 Portal 主首頁 Dashboard
# ==========================================================
@login_required(login_url='users:login')
def student_index(request):
    """學生端首頁 Dashboard (🔒 必須登入)"""
    student = _get_current_student_or_fallback(request)
    
    if not student:
        messages.error(request, "資料庫內目前沒有任何學生資料，請先至行政端或後台建立。")
        return redirect("office:office_index")
            
    # 🟢 核心優化：加上 select_related('course') 避免 N+1 查詢，一口氣拉出所有選課
    enrollments = Enrollment.objects.filter(student=student).select_related('course', 'course__teacher')
    
    context = {
        "student": student,
        "school_class": student.school_class,
        "total_courses": enrollments.count(),
        "enrollments": enrollments,  # 提供給 student.html 做迴圈渲染
        "courses": [e.course for e in enrollments], # 相容部分直接讀取 course 列表的前端
    }
    return render(request, 'students/student.html', context)


# ==========================================================
# 🎓 2. 學生端 - 週課表 / 時間表
# ==========================================================
@login_required(login_url='users:login')
def timetable_view(request):
    """2. 學生課表/時間表視圖 (🔒 必須登入)"""
    student = _get_current_student_or_fallback(request)
    
    if not student:
        messages.error(request, "資料庫內目前沒有任何學生資料，請先至行政端或後台建立。")
        return redirect("office:office_index")
        
    # 🟢 織網多對多：精準撈出該學生在 Enrollment 裡綁定的所有課程物件
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    my_courses = [e.course for e in enrollments]
    
    context = {
        "student": student,
        "school_class": student.school_class,
        "courses": my_courses,  # 傳送真實選課列表給功課表前端
        "enrollments": enrollments,
    }
    return render(request, 'students/timetable.html', context)


# ==========================================================
# 🎓 3. 學生端 - 線上選課
# ==========================================================
@login_required(login_url='users:login')
def enroll_view(request):
    """3. 學生端 - 線上選課系統 (🔒 必須登入，支援 GET 顯示與 POST 寫入)"""
    student = _get_current_student_or_fallback(request)
    
    if not student:
        messages.error(request, "資料庫內目前沒有任何學生資料，請先至行政端或後台建立。")
        return redirect("office:office_index")

    # 📥 【POST 動作】：當學生點擊「確認選課」按鈕時
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        course = get_object_or_404(Course, id=course_id)
        
        # 🛡️ 鋼鐵防線 1：檢查是不是早就選過了，防止重覆選課導致資料庫崩潰
        exists = Enrollment.objects.filter(student=student, course=course).exists()
        if exists:
            messages.warning(request, f"你已經選修過【{course.name}】囉！")
        else:
            # 🟢 真金白銀寫入：在協調表中建立連結，預設出席率 100%
            Enrollment.objects.create(
                student=student,
                course=course,
                attendance_rate=100.00
            )
            messages.success(request, f"🎉 恭喜！成功選修課程：【{course.name}】！")
        
        return redirect('students:enroll') # 重新導向，重新刷新選課頁面

    # 📤 【GET 動作】：正常載入網頁時
    # 💡 核心演算法：過濾掉「已經選過的課程」，只秀出還沒選的課
    enrolled_course_ids = Enrollment.objects.filter(student=student).values_list('course_id', flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_course_ids).select_related('teacher')
    
    # 順便撈出已經選的課，方便在網頁下方做個「已選清單」對照
    my_enrollments = Enrollment.objects.filter(student=student).select_related('course')

    context = {
        "student": student,
        "school_class": student.school_class,
        "available_courses": available_courses,  # 還可以選的課
        "my_enrollments": my_enrollments,        # 目前已經選的課
    }
    return render(request, 'students/enroll.html', context)
# @login_required(login_url='users:login')
# def enroll_view(request):
#     """3. 學生端 - 線上選課系統 (🔒 必須登入)"""
#     student = _get_current_student_or_fallback(request)
    
#     if not student:
#         messages.error(request, "資料庫內目前沒有任何學生資料，請先至行政端或後台建立。")
#         return redirect("office:office_index")
        
#     context = {
#         "student": student,
#         "school_class": student.school_class,
#     }
#     return render(request, 'students/enroll.html', context)


# ==========================================================
# 🎓 4. 學生端 - 核心成績單 / 分數報告
# ==========================================================
@login_required(login_url='users:login')
def grades_report_view(request):
    """4. 學生分數報告/成績單視圖 (🔒 必須登入)"""
    student = _get_current_student_or_fallback(request)
    
    if not student:
        messages.error(request, "資料庫內目前沒有任何學生資料，請先至行政端或後台建立。")
        return redirect("office:office_index")
        
    # 🟢 真金白銀防線：把帶有 score（分數）的 Enrollment 紀錄整條拋給前端
    enrollments = Enrollment.objects.filter(student=student).select_related('course', 'course__teacher')
    
    # 📈 即時動態計算學生的【平均分】與【平均出席率】
    valid_scores = [e.score for e in enrollments if e.score is not None]
    valid_attendance = [e.attendance_rate for e in enrollments if e.attendance_rate is not None]
    
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
    avg_attendance = sum(valid_attendance) / len(valid_attendance) if valid_attendance else 100.0
    
    context = {
        "student": student,
        "school_class": student.school_class,
        "enrollments": enrollments,       # 建議前端標準迴圈變數
        "grades": enrollments,            # 雙重相容：防止前端使用 grades 變數
        "avg_score": avg_score,           # 即時平均分
        "avg_attendance": avg_attendance, # 即時平均出席率
    }
    return render(request, 'students/grades_report.html', context)
# ==========================================================
# 🎓 5. 學生端 - 個人資料與密碼修改 (100% 軟柿子速攻)
# ==========================================================
@login_required(login_url='users:login')
def student_profile_view(request):
    """學生個人資料與安全密碼修改視圖"""
    student = _get_current_student_or_fallback(request)
    
    if not student:
        messages.error(request, "Ther is currently no student information in the database.")
        return redirect("office:office_index")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # 🛡️ 安全防線：檢查密碼有無填寫與是否一致
        if not new_password or not confirm_password:
            messages.error(request, "❌ Please fill in all password fields completely.")
        elif new_password != confirm_password:
            messages.error(request, "❌ The two passwords entered do not match, please check again")
        else:
            # 🟢 真金白銀寫入：直接更新該學生的密碼欄位並儲存
            student.password = new_password
            student.save()
            messages.success(request, "🔒 Password changed successfully ! Use the new password next time you login")
            return redirect('students:profile')

    context = {
        "student": student,
        "school_class": student.school_class,
    }
    return render(request, 'students/profile.html', context)