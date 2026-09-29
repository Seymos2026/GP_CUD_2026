from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('export-all-students/', views.export_all_students_grades, name='export_all_students_grades'),
    path('<int:project_id>/weekly/', views.weekly_progress_list, name='weekly_progress_list'),
    path('<int:project_id>/weekly/new/', views.weekly_progress_form, name='weekly_progress_create'),
    path('<int:project_id>/weekly/<int:report_id>/', views.weekly_progress_form, name='weekly_progress_edit'),
]
