from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Project, Task, Attachment
from .serializers import ProjectSerializer, TaskSerializer, AttachmentSerializer
from .tasks import send_email_notification
from users.permissions import IsManager, IsManagerOrDeveloper

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['owner']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.annotate(tasks_count=Count('tasks'))
        
        if user.role == 'MANAGER':
            return queryset.filter(owner=user)
        
        return queryset.filter(tasks__assignee=user).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project', 'assignee']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.select_related('assignee', 'project').prefetch_related('attachments')
        
        if user.role == 'MANAGER':
            # Managers see tasks in their projects
            return queryset.filter(project__owner=user)
        
        # Others see tasks assigned to them
        return queryset.filter(assignee=user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOrDeveloper()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save()
        # Trigger background task
        send_email_notification.delay(
            self.request.user.id,
            'New Task Created via API',
            f"You have successfully created a new task: {instance.title}"
        )

class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can see attachments for tasks they can see
        user = self.request.user
        if user.role == 'MANAGER':
            return Attachment.objects.filter(task__project__owner=user)
        return Attachment.objects.filter(task__assignee=user)

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
