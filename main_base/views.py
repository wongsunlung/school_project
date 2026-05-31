from django.shortcuts import render

def index(request):
    """全站純英文大首頁入口：不夾雜複雜邏輯，確保一秒秒開"""
    return render(request, 'index.html')
