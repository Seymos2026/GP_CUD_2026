from django.urls import path
from . import views

app_name = 'rubrics'

urlpatterns = [
    path('', views.rubric_list, name='rubric_list'),
    path('<int:rubric_id>/', views.rubric_detail, name='rubric_detail'),
    path('import/', views.rubric_import, name='rubric_import'),
    path('download-template/', views.download_rubric_template, name='download_template'),
    path('<int:rubric_id>/delete/', views.rubric_delete, name='rubric_delete'),
]
