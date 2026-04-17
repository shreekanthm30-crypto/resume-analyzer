from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<int:analysis_id>/', views.download_analysis, name='download_analysis'),
    path('history/', views.analysis_history, name='analysis_history'),
]