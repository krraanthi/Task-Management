import pytest
from rest_framework import status
from rest_framework.test import APIClient
from .factories import UserFactory, ProjectFactory, TaskFactory
from tasks.models import Project, Task

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def manager_user():
    return UserFactory(role='MANAGER')

@pytest.fixture
def developer_user():
    return UserFactory(role='DEVELOPER')

@pytest.mark.django_db
class TestProjectAPI:
    def test_list_projects_authenticated(self, api_client, manager_user):
        project = ProjectFactory(owner=manager_user)
        api_client.force_authenticate(user=manager_user)
        
        response = api_client.get('/api/projects/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == project.name

    def test_create_project_manager_only(self, api_client, manager_user, developer_user):
        api_client.force_authenticate(user=developer_user)
        response = api_client.post('/api/projects/', {'name': 'New Project'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        api_client.force_authenticate(user=manager_user)
        response = api_client.post('/api/projects/', {'name': 'Manager Project'})
        assert response.status_code == status.HTTP_201_CREATED
        assert Project.objects.filter(name='Manager Project').exists()

@pytest.mark.django_db
class TestTaskAPI:
    def test_create_task_notification_triggered(self, api_client, developer_user, mocker):
        # Mocking the delay() method on the celery task
        mock_task = mocker.patch('tasks.api_views.send_email_notification.delay')
        
        project = ProjectFactory()
        api_client.force_authenticate(user=developer_user)
        
        data = {
            'title': 'Test Task',
            'project': project.id,
            'status': 'TODO',
            'priority': 'MEDIUM'
        }
        
        response = api_client.post('/api/tasks/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert mock_task.called
