from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('project/<int:project_id>/', views.project_report, name='project_report'),
    path('project/<int:project_id>/excel/', views.export_excel, name='export_excel'),
    path('project/<int:project_id>/pdf/', views.export_pdf, name='export_pdf'),
]
