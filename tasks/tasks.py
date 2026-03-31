from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
import csv
import io
import time

User = get_user_model()

@shared_task
def daily_overdue_tasks_summary():
    """
    Periodic task to send a summary of overdue tasks to users.
    """
    from .models import Task
    today = timezone.now().date()
    users = User.objects.all()
    
    for user in users:
        overdue_tasks = Task.objects.filter(
            assignee=user,
            due_date__lt=today,
            status__in=['TODO', 'IN_PROGRESS']
        )
        
        if overdue_tasks.exists():
            task_list = "\n".join([f"- {task.title} (Due: {task.due_date})" for task in overdue_tasks])
            send_mail(
                'Daily Overdue Tasks Summary',
                f"Hi {user.username},\n\nYou have the following overdue tasks:\n\n{task_list}\n\nPlease update them as soon as possible.",
                'noreply@protasker.com',
                [user.email],
                fail_silently=False,
            )
    
    return f"Processed summaries for {users.count()} users."

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_id, subject, message):
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject,
            message,
            'noreply@protasker.com',
            [user.email],
            fail_silently=False,
        )
        return f"Email sent to {user.email}"
    except Exception as exc:
        # Retry in 5 minutes (300 seconds) if there's a failure
        raise self.retry(exc=exc, countdown=300)

@shared_task
def generate_project_report(project_id):
    # Simulate a heavy task (e.g., generating a complex report)
    from .models import Project
    project = Project.objects.get(id=project_id)
    tasks = project.tasks.all()
    
    # In a real app, you might save this to a file or send it via email
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Status', 'Priority', 'Due Date'])
    
    for task in tasks:
        writer.writerow([task.title, task.status, task.priority, task.due_date])
    
    # Simulate processing time
    time.sleep(2)
    
    return f"Report generated for {project.name} with {tasks.count()} tasks."
