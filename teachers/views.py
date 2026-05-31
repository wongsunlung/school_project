from django.shortcuts import render

def teacher_index(request):
    """教師端 Portal 首頁"""
    return render(request, 'teachers/teacher.html')

def attendance_list(request):
    """教師端 - 出勤紀錄"""
    return render(request, 'teachers/attendance.html')

def grades_list(request):
    """教師端 - 成績輸入"""
    return render(request, 'teachers/grades.html')
