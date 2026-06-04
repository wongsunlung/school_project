import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login

# 📋 精準引入 main_base 底下的 Student 與 Teacher 模型
from main_base.models import Student, Teacher 

# ==========================================================
# 📩 【功能一】登記視圖：register_view（物理歸位，一秒解死機）
# ==========================================================
def register_view(request):
    """
    接收登記網頁的 POST 數據
    並將名字、Email、性別、專長、不加密的密碼真金白銀寫入新資料庫
    """
    if request.method == "POST":
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # 💡 核心新增 1：真金白銀撈取前端傳來的性別與專長數據
        gender = request.POST.get('gender')
        specialty = request.POST.get('specialty')

        # 這裡維持原本的基礎必填欄位檢查 (不把 specialty 放進來，因為學生沒有 specialty)
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

            # 💡 備註：如果你的 Student 模型也有 gender 欄位，可以在下方順便加上 "gender=gender,"
            Student.objects.create(
                student_id=random_student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                is_active=True
            )
            messages.success(request, f"Student {first_name} registered successfully! Please login.")
            return redirect('users:login')

        # ─── 老師登記分支 ───
        elif role == 'teacher':
            if Teacher.objects.filter(email=email).exists():
                messages.error(request, "This Email Address is already registered as a teacher.")
                return render(request, 'users/register.html')
            
            # 💡 核心修正 2：在建立老師資料時，精準將性別與專長寫入資料庫
            Teacher.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                gender=gender,         # ✨ 補上性別欄位
                specialty=specialty    # ✨ 補上專長欄位
            )
            messages.success(request, f"Teacher {first_name} registered successfully! Please login.")
            return redirect('users:login')

    return render(request, 'users/register.html')
# def register_view(request):
#     """
#     接收登記網頁的 POST 數據
#     並將名字、Email、不加密的密碼真金白銀寫入新資料庫
#     """
#     if request.method == "POST":
#         role = request.POST.get('role')
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         if not all([role, first_name, last_name, email, password]):
#             messages.error(request, "All fields are required.")
#             return render(request, 'users/register.html')

#         # ─── 學生登記分支 ───
#         if role == 'student':
#             if Student.objects.filter(email=email).exists():
#                 messages.error(request, "This Email Address is already registered as a student.")
#                 return render(request, 'users/register.html')
            
#             random_student_id = f"STU{random.randint(10000, 99999)}"
#             while Student.objects.filter(student_id=random_student_id).exists():
#                 random_student_id = f"STU{random.randint(10000, 99999)}"

#             Student.objects.create(
#                 student_id=random_student_id,
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 password=password,
#                 is_active=True
#             )
#             messages.success(request, f"Student {first_name} registered successfully! Please login.")
#             return redirect('users:login')

#         # ─── 老師登記分支 ───
#         elif role == 'teacher':
#             if Teacher.objects.filter(email=email).exists():
#                 messages.error(request, "This Email Address is already registered as a teacher.")
#                 return render(request, 'users/register.html')
            
#             Teacher.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 password=password
                
#             )
#             messages.success(request, f"Teacher {first_name} registered successfully! Please login.")
#             return redirect('users:login')

#     return render(request, 'users/register.html')


# ==========================================================
# 🔑 【功能二】登入驗證視圖：login_view（含 Superuser 特權密道）
# ==========================================================
def login_view(request):
    """
    終極指揮中心：完美接收 name="username" 與 name="password"
    支援最高管理員特權穿透，同時向下相容普通師生名字拆解與硬對齊
    """
    if request.method == "POST":
        role = request.POST.get('role')
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        if not username_input or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'users/login.html')

        # 👑 🌟 【最高防禦：Superuser 特權密道一槍定位】 🌟 👑
        # 拿前端輸入的名字去內建 User 表撈取最高管理員
        superuser_check = User.objects.filter(username=username_input.strip(), is_superuser=True).first()
        
        if superuser_check and superuser_check.check_password(password):
            auth_login(request, superuser_check) # 激活內建認證
            
            request.session['role'] = role 
            request.session['user_name'] = f"Superuser: {superuser_check.username}"
            
            # 🚀 補齊跳轉邏輯：根據勾選的身份，精準重導向，絕不殘留輸入框！
            if role == 'student':
                request.session['student_id'] = 1 
                return redirect('/students/report/')
            elif role == 'teacher':
                request.session['teacher_id'] = 1 
                return redirect('/teachers/grades/')
            elif role == 'office':
                # 🌟 一槍定位：如果是行政端/管理員登入，重導向到管理後台網址
                # 請確認底下的 '/office/dashboard/' 是否符合你專案的實際後台網址
                return redirect('/office/')#這是重點

        # 🧠 若不是管理員，則走回原本嚴謹的「師生名字拆解與硬對齊」邏輯
        name_parts = username_input.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
        else:
            first_name = username_input.strip()
            last_name = ""

        # ─── 學生登入比對report ───
        if role == 'student':
            matched_student = Student.objects.filter(
                first_name__iexact=first_name, last_name__iexact=last_name, password=password
            ).first()
            if not matched_student and not last_name:
                matched_student = Student.objects.filter(first_name__iexact=first_name, password=password).first()

            if matched_student:
                user_obj, _ = User.objects.get_or_create(
                    username=f"{matched_student.first_name}_{matched_student.last_name}".lower().replace(" ", "_"), 
                    email=matched_student.email
                )
                auth_login(request, user_obj)
                request.session['role'] = 'student'
                request.session['student_id'] = matched_student.id
                request.session['user_name'] = f"{matched_student.first_name} {matched_student.last_name}"
                return redirect('/students/')

        # ─── 老師登入比對 /grades───
        elif role == 'teacher':
            matched_teacher = Teacher.objects.filter(
                first_name__iexact=first_name, last_name__iexact=last_name, password=password
            ).first()
            if not matched_teacher and not last_name:
                matched_teacher = Teacher.objects.filter(first_name__iexact=first_name, password=password).first()

            if matched_teacher:
                user_obj, _ = User.objects.get_or_create(
                    username=f"{matched_teacher.first_name}_{matched_teacher.last_name}".lower().replace(" ", "_"), 
                    email=matched_teacher.email
                )
                auth_login(request, user_obj)
                request.session['role'] = 'teacher'
                request.session['teacher_id'] = matched_teacher.id
                request.session['user_name'] = f"{matched_teacher.first_name} {matched_teacher.last_name}"
                return redirect('/teachers/')

        # 如果連角色都沒選對，或者沒有匹配到任何分支，才判定失敗
        messages.error(request, "Authentication failed: Name and password do not match!")
        return render(request, 'users/login.html')

    return render(request, 'users/login.html')
