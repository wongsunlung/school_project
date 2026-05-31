from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib import auth
# 🌟 嚴格引入中央資料庫模型，確保註冊資料真金白銀寫進去
from main_base.models import Teacher, Student

def login_view(request):
    """1. 登入角色分流視圖"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            if role == 'office': return redirect("office:index")
            elif role == 'teacher': return redirect("teachers:index")
            elif role == 'student': return redirect("students:timetable")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("users:login")
    return render(request, "users/login.html")


def register_view(request):
    """🌟 2. 新生與新聘老師註冊登記視圖（100% 寫入資料庫，絕不糊弄）"""
    if request.method == "POST":
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email', '').lower()

        # ─── A 狀況：如果是新聘老師登記 ───
        if role == 'teacher':
            gender = request.POST.get('gender', 'O')
            specialty = request.POST.get('specialty', '')
            
            # 嚴格重複校驗
            if Teacher.objects.filter(email=email).exists():
                messages.error(request, f"The email {email} has already been registered as faculty.")
                return redirect("users:register")
            
            # 🌟 正式寫入資料庫 school_teachers 資料表！
            Teacher.objects.create(
                first_name=first_name, last_name=last_name, 
                email=email, gender=gender, specialty=specialty,
                is_active=False # 預設 False，留給行政端未來點擊審核激活
            )
            messages.success(request, f"Faculty registration submitted successfully! Prof. {first_name} is now written to database, pending admin review.")
            return redirect("main_base:index")

        # ─── B 狀況：如果是新生登記 ───
        elif role == 'student':
            # 為新生自動生成一個今年年份開頭的專屬學號，格式看齊您的 STU-2026-xxx
            current_year = "2026"
            next_id = Student.objects.count() + 1
            student_id = f"STU-{current_year}-{next_id:03d}"
            
            if Student.objects.filter(email=email).exists():
                messages.error(request, f"The email {email} has already been registered as a student.")
                return redirect("users:register")

            # 🌟 正式寫入資料庫 school_students 資料表！
            Student.objects.create(
                student_id=student_id, first_name=first_name, 
                last_name=last_name, email=email,
                school_class=None # 預設沒有班級，留給行政端未來點擊分班審核
            )
            messages.success(request, f"Student registration submitted! Your assigned ID is {student_id}. Written to database, pending admin class placement.")
            return redirect("main_base:index")

    return render(request, "users/register.html")
