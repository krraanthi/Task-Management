from rest_framework import serializers
from .models import Project, Task, Attachment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'task', 'file', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['uploaded_at', 'uploaded_by']

class TaskSerializer(serializers.ModelSerializer):
    assignee_detail = UserSerializer(source='assignee', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 
            'due_date', 'project', 'assignee', 'assignee_detail',
            'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ProjectSerializer(serializers.ModelSerializer):
    owner_detail = UserSerializer(source='owner', read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'owner_detail', 
            'tasks', 'tasks_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
