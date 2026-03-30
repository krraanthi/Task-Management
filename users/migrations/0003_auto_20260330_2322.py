from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    
    # Define groups
    manager_group, _ = Group.objects.get_or_create(name='Manager')
    developer_group, _ = Group.objects.get_or_create(name='Developer')
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')

def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Manager', 'Developer', 'Viewer']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_role_alter_user_id'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
