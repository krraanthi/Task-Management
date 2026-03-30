from django.urls import path
from .views import (
    ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    TaskCreateView, TaskUpdateView, TaskDeleteView
)

urlpatterns = [
    # Projects
    path('', ProjectListView.as_view(), name='project-list'),
    path('project/new/', ProjectCreateView.as_view(), name='project-create'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('project/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
    
    # Tasks
    path('project/<int:project_id>/task/new/', TaskCreateView.as_view(), name='task-create'),
    path('task/<int:pk>/edit/', TaskUpdateView.as_view(), name='task-update'),
    path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
]
