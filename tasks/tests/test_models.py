import pytest
from .factories import UserFactory, ProjectFactory, TaskFactory
from tasks.models import Project, Task

@pytest.mark.django_db
class TestTaskModels:
    def test_task_str_representation(self):
        task = TaskFactory(title="Fix Bug")
        assert str(task) == "Fix Bug"

    def test_project_task_count_annotation(self):
        project = ProjectFactory()
        TaskFactory.create_batch(3, project=project)
        
        # We need to re-fetch with annotation as per our ViewSet logic
        from django.db.models import Count
        p = Project.objects.annotate(tasks_count=Count('tasks')).get(id=project.id)
        assert p.tasks_count == 3
