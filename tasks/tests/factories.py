import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from tasks.models import Project, Task

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    role = 'DEVELOPER'

class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project
    
    name = factory.Faker('company')
    owner = factory.SubFactory(UserFactory)

class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
    
    title = factory.Faker('sentence')
    project = factory.SubFactory(ProjectFactory)
