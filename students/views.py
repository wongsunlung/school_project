from django.shortcuts import render

def student_index(request):
    """學生端 Hub 首頁"""
    return render(request, 'students/student.html')

def timetable_view(request):
    """學生端 - 課表網頁"""
    return render(request, 'students/timetable.html')

def grades_report_view(request):
    """學生端 - 成績查詢（對齊您的 grades_report 檔名）"""
    return render(request, 'students/grades_report.html')

def enroll_view(request):
    """學生端 - 線上選課"""
    return render(request, 'students/enroll.html')
