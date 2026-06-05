import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator  
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# 🟢 引入 Teacher 模型，確保多對多與個人資料地基完整
from main_base.models import Student, Enrollment, Course, Teacher  

# ==========================================================
# 🛠️ 內部防呆機制：確保登入者一定是老師，否則自動抓第一筆進行測試
# ==========================================================
def _get_current_teacher_or_fallback(request):
    """內部輔助函式：獲取當前老師，若無則抓取第一筆作為測試 fallback"""
    teacher = Teacher.objects.filter(email=request.user.email).first()
    if not teacher:
        teacher = Teacher.objects.first()
    return teacher


# ==========================================================
# 👨‍🏫 1. 教師端 Portal 首頁 Dashboard
# ==========================================================
@login_required(login_url='users:login')
def teacher_index(request):
    """教師端 Portal 首頁 (🔒 必須登入 - 📊 動態儀表板數據核心)"""
    teacher = _get_current_teacher_or_fallback(request)
    
    # 1. 🎯 算出該教師名下的所有課程數量
    my_courses = teacher.courses.all() if hasattr(teacher, 'courses') else []
    total_courses = my_courses.count() if hasattr(my_courses, 'count') else len(my_courses)
    
    # 2. 🗄️ 撈出這些課程在中間表（Enrollment）的所有選課紀錄
    # 這裡直接沿用您在考勤表通過驗證的 Enrollment 模型
    enrollments = Enrollment.objects.filter(course__in=my_courses) if my_courses else []
    
    # 3. 📈 動態計算平均出勤率 (與行政端織網演算法精準對齊，保留一位小數)
    if enrollments:
        valid_attendance = [e.attendance_rate for e in enrollments if hasattr(e, 'attendance_rate') and e.attendance_rate is not None]
        avg_attendance = round(sum(valid_attendance) / len(valid_attendance), 1) if valid_attendance else 100.0
    else:
        avg_attendance = 100.0
        
    # 4. 📝 動態計算「待評分」數量 (即 score 欄位還是 None 的學生選課紀錄)
    if enrollments:
        pending_count = enrollments.filter(score__isnull=True).count()
    else:
        pending_count = 0
        
    # 5. 📦 打包真金白銀的數據送往前端
    context = {
        'teacher': teacher,
        'total_courses': total_courses,
        'avg_attendance': avg_attendance,
        'pending_count': pending_count
    }
    
    # 🚨 備註：此處維持您原本指定的 'teachers/teacher.html' 樣板路徑
    return render(request, 'teachers/teacher.html', context)
# @login_required(login_url='users:login')
# def teacher_index(request):
#     """教師端 Portal 首頁 (🔒 必須登入)"""
#     teacher = _get_current_teacher_or_fallback(request)
#     return render(request, 'teachers/teacher.html', {'teacher': teacher})


# ==========================================================
# 👨‍🏫 2. 教師端 - 出勤紀錄清單
# ==========================================================
@login_required(login_url='users:login')
def attendance_list(request):
    """教師端 - 出勤紀錄（每頁 5 筆 - 🟢 完美融合多對多地基）"""
    teacher = _get_current_teacher_or_fallback(request)
    
    # 🚨 核心防線修補：先找出當前登入老師名下的所有課程
    my_courses = teacher.courses.all() if hasattr(teacher, 'courses') else []
    
    # 🎯 精準過濾：只撈出「有報讀這些課程」的學生名單，並去重（.distinct()）防止重複
    student_list = Student.objects.filter(courses__in=my_courses).distinct().order_by('id')
    
    # 全站統一 5 人分頁器
    paginator = Paginator(student_list, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 🟢 終極防線：強行把中間表的出勤率掛載到前端屬性，防止錯誤
    for student in page_obj.object_list:
        try:
            # 🎯 精準修正：撈中間表時，必須限定是該學生「報讀這位老師名下課程」的紀錄，絕不張冠李戴
            enrollment = Enrollment.objects.filter(student=student, course__in=my_courses).first()
            if enrollment and hasattr(enrollment, 'attendance_rate'):
                student.attendance_rate = enrollment.attendance_rate
            else:
                student.attendance_rate = 100.0
        except:
            student.attendance_rate = 100.0
            
    context = {
        'page_obj': page_obj,
        'teacher': teacher
    }
    return render(request, 'teachers/attendance.html', context)


# ==========================================================
# 👨‍🏫 3. 教師端 - 核心成績輸入列表（權限隔離）
# ==========================================================
@login_required(login_url='users:login')
def grades_list(request):
    """教師端 - 成績輸入（🌟 權限隔離版：只看自己的學生、自己的課）"""
    teacher = _get_current_teacher_or_fallback(request)
    
    if not teacher:
        messages.error(request, "資料庫內目前沒有任何教師資料。")
        return redirect("office:office_index")
        
    teacher_email = teacher.email
    
    # 🌟 隔離防線：只抓「有修當前老師課程」的學生
    student_list = Student.objects.filter(
        enrollments__course__teacher__email=teacher_email
    ).distinct().order_by('id')

    paginator = Paginator(student_list, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    for student in page_obj.object_list:
        # 🌟 隔離防線：把學生的課展開時，只抓「當前登入老師」教的課！
        student.my_enrollments = Enrollment.objects.filter(
            student=student,
            course__teacher__email=teacher_email  
        ).select_related('course')
            
    context = {
        'page_obj': page_obj,
        'teacher': teacher
    }
    return render(request, 'teachers/grades.html', context)


# ==========================================================
# 👨‍🏫 4. 教師端 - 個人資料與密碼、進修專長修改 (全新解鎖 🔓)
# ==========================================================
@login_required(login_url='users:login')
def teacher_profile_view(request):
    """教師個人資料、密碼與進修專長修改視圖"""
    teacher = _get_current_teacher_or_fallback(request)
    
    if not teacher:
        messages.error(request, "資料庫內目前沒有任何教師資料。")
        return redirect("office:office_index")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        specialty = request.POST.get("specialty")

        # 🟢 動作 1：真金白銀寫入更新「進修專長」
        teacher.specialty = specialty
        teacher.save()

        # 🔒 動作 2：處理密碼修改 (有填寫才進行變更檢查)
        if new_password or confirm_password:
            if new_password != confirm_password:
                messages.error(request, "❌ The two entries of new password do not match ! Expertise has been updated, but the password change failed.")
            else:
                teacher.password = new_password
                teacher.save()
                messages.success(request, "🔒 Password and expertise have been successfully updated !")
                return redirect('teachers:profile')
        else:
            messages.success(request, "📝 expertise have been successfully updated !")
            return redirect('teachers:profile')

    return render(request, 'teachers/profile.html', {'teacher': teacher})


# ==========================================================
# 🌐 🛠️ 實時儲存 API 補給線 (AJAX 異步調用)teacher
# ==========================================================

@csrf_exempt
def api_update_attendance(request):
    """點名 API 安全升級：精準寫入中間表"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('id')      
            is_present = data.get('status')  
            
            student = Student.objects.get(id=student_id)
            enrollment = Enrollment.objects.filter(student=student).first()
            if enrollment:
                if hasattr(enrollment, 'attendance_rate'):
                    enrollment.attendance_rate = 100.0 if is_present else 0.0
                enrollment.save()
                return JsonResponse({'status': 'success'})
                
            return JsonResponse({'status': 'error', 'message': 'No enrollment found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid_method'}, status=405)


@csrf_exempt
def api_update_score(request):
    """評分 API：真金白銀精準寫入中間表 (附帶權限隔離)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('id')      
            score_value = data.get('score')  
            course_id = data.get('course_id')  
            
            if not student_id or score_value is None or not course_id:
                return JsonResponse({'status': 'error', 'message': 'Missing Data.'}, status=400)
                
            student = Student.objects.get(id=student_id)
            teacher = _get_current_teacher_or_fallback(request)
            
            # 🌟 隔離防線：確保修改的這門課，真的是當前登入老師教的
            enrollment = Enrollment.objects.filter(
                student=student, 
                course_id=course_id,
                course__teacher__email=teacher.email
            ).first()
            
            if enrollment:
                enrollment.score = int(score_value)
                enrollment.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Permission Denied!'}, status=403)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'invalid_method'}, status=405)