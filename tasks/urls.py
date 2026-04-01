from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    TaskCreateView, TaskUpdateView, TaskDeleteView
)
from .api_views import ProjectViewSet, TaskViewSet, AttachmentViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='api-project')
router.register(r'tasks', TaskViewSet, basename='api-task')
router.register(r'attachments', AttachmentViewSet, basename='api-attachment')

urlpatterns = [
    # API
    path('api/', include(router.urls)),
    
    # Projects (HTML Views)
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
