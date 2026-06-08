import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login

# 📋 精準引入 main_base 底下的 Student 與 Teacher 模型
from main_base.models import Student, Teacher 

# ==========================================================
# 📩 【功能一】登記視圖：register_view（修正：預設不啟用）
# ==========================================================
def register_view(request):
    """
    接收登記網頁的 POST 數據
    並將名字、Email、性別、專長、不加密的密碼寫入資料庫
    🚨 安全修正：新註冊的師生 is_active 預設一律為 False！
    """
    if request.method == "POST":
        print("====== 收到 POST 資料了！ ======")
        print(request.POST)
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        gender = request.POST.get('gender')
        specialty = request.POST.get('specialty')

        if not all([role, first_name, last_name, email, password]):
            messages.error(request, "All fields are required.")
            return render(request, 'users/register.html')

        # ─── 學生登記分支 ───
        if role == 'student':
            if Student.objects.filter(email=email).exists():
                messages.error(request, "This Email Address is already registered as a student.")
                return render(request, 'users/register.html')
            
            random_student_id = f"STU{random.randint(10000, 99999)}"
            while Student.objects.filter(student_id=random_student_id).exists():
                random_student_id = f"STU{random.randint(10000, 99999)}"

            # 🚨 漏洞修補 1：將原本的 is_active=True 改為 False
            Student.objects.create(
                student_id=random_student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                is_active=False  # ✨ 新生需要審核，預設不啟用
            )
            messages.warning(request, f"學生 {first_name} 登記成功！目前為【訪客審核狀態】，請等待管理員啟用帳號後再行登入。")
            return redirect('users:login')

        # ─── 老師登記分支 ───
        elif role == 'teacher':
            if Teacher.objects.filter(email=email).exists():
                messages.error(request, "This Email Address is already registered as a teacher.")
                return render(request, 'users/register.html')
            
            # 🚨 漏洞修補 2：幫老師也補上 is_active=False 欄位（請確保您的 Teacher Model 有此欄位）
            Teacher.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                gender=gender,         
                specialty=specialty,
                is_active=False  # ✨ 新聘老師需要審核，預設不啟用
            )
            messages.warning(request, f"老師 {first_name} 登記成功！目前為【訪客審核狀態】，請等待行政端啟用帳號。")
            return redirect('users:login')

    return render(request, 'users/register.html')


# ==========================================================
# 🔑 【功能二】登入驗證視圖：login_view（含訪客攔截關卡）
# ==========================================================
def login_view(request):
    """
    終極指揮中心：嚴格檢查帳密
    🚨 安全修正：增加 is_active=False 攔截，未啟用者拒絕發放核心工具權限，維持訪客提示。
    """
    if request.method == "POST":
        role = request.POST.get('role')
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        if not username_input or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'users/login.html')

        # 👑 【最高防禦：Superuser 特權密道】
        superuser_check = User.objects.filter(username=username_input.strip(), is_superuser=True).first()
        
        if superuser_check and superuser_check.check_password(password):
            auth_login(request, superuser_check) 
            request.session['role'] = role 
            request.session['user_name'] = f"Superuser: {superuser_check.username}"
            
            if role == 'student':
                request.session['student_id'] = 1 
                return redirect('/students/report/')
            elif role == 'teacher':
                request.session['teacher_id'] = 1 
                return redirect('/teachers/grades/')
            elif role == 'office':
                return redirect('/office/')

        # 🧠 普通師生名字拆解邏輯
        name_parts = username_input.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
        else:
            first_name = username_input.strip()
            last_name = ""

        # ─── 學生登入比對 ───
        if role == 'student':
            matched_student = Student.objects.filter(
                first_name__iexact=first_name, last_name__iexact=last_name, password=password
            ).first()
            if not matched_student and not last_name:
                matched_student = Student.objects.filter(first_name__iexact=first_name, password=password).first()

            if matched_student:
                # 🚨 漏洞修補 3：攔截未啟用的學生，強制阻斷，保持訪客限制
                if not getattr(matched_student, 'is_active', True):
                    messages.error(request, "您的帳號尚未啟用（審核中），目前僅具備【訪客身份】，無法進入學生系統！")
                    return render(request, 'users/login.html')

                # 只有 active 是 True 的學生才能拿到通行證
                user_obj, _ = User.objects.get_or_create(
                    username=f"{matched_student.first_name}_{matched_student.last_name}".lower().replace(" ", "_"), 
                    email=matched_student.email
                )
                auth_login(request, user_obj)
                request.session['role'] = 'student'
                request.session['student_id'] = matched_student.id
                request.session['user_name'] = f"{matched_student.first_name} {matched_student.last_name}"
                return redirect('/students/')

        # ─── 老師登入比對 ───
        elif role == 'teacher':
            matched_teacher = Teacher.objects.filter(
                first_name__iexact=first_name, last_name__iexact=last_name, password=password
            ).first()
            if not matched_teacher and not last_name:
                matched_teacher = Teacher.objects.filter(first_name__iexact=first_name, password=password).first()

            if matched_teacher:
                # 🚨 漏洞修補 4：攔截未啟用的老師，強制阻斷
                if not getattr(matched_teacher, 'is_active', True):
                    messages.error(request, "您的教師帳號尚未啟用（審核中），目前僅具備【訪客身份】，無法進入管理系統！")
                    return render(request, 'users/login.html')

                user_obj, _ = User.objects.get_or_create(
                    username=f"{matched_teacher.first_name}_{matched_teacher.last_name}".lower().replace(" ", "_"), 
                    email=matched_teacher.email
                )
                auth_login(request, user_obj)
                request.session['role'] = 'teacher'
                request.session['teacher_id'] = matched_teacher.id
                request.session['user_name'] = f"{matched_teacher.first_name} {matched_teacher.last_name}"
                return redirect('/teachers/')

        messages.error(request, "Authentication failed: Name and password do not match!")
        return render(request, 'users/login.html')

    return render(request, 'users/login.html')