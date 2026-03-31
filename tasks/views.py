from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Project, Task
from .tasks import send_email_notification

# Project Views
@method_decorator(cache_page(60 * 15), name='dispatch')
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'tasks/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # Optimization: Annotate task count to avoid N+1 queries in the template
        return Project.objects.filter(owner=self.request.user).annotate(
            tasks_count=Count('tasks')
        )

class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'tasks/project_detail.html'

    def get_queryset(self):
        # Optimization: Prefetch tasks and select related assignee to get everything in fewer queries
        return Project.objects.prefetch_related(
            'tasks__assignee'
        ).all()

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'tasks/project_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('project-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    template_name = 'tasks/project_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('project-list')

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'tasks/project_confirm_delete.html'
    success_url = reverse_lazy('project-list')

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

# Task Views
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'status', 'priority', 'due_date', 'assignee']

    def form_valid(self, form):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        form.instance.project = project
        response = super().form_valid(form)
        
        # Trigger background task
        send_email_notification.delay(
            self.request.user.id,
            'New Task Created',
            f"You have successfully created a new task: {self.object.title}"
        )
        return response

    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={'pk': self.kwargs['project_id']})

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'status', 'priority', 'due_date', 'assignee']

    def test_func(self):
        task = self.get_object()
        return self.request.user == task.project.owner

    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={'pk': self.object.project.id})

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'

    def test_func(self):
        task = self.get_object()
        return self.request.user == task.project.owner

    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={'pk': self.object.project.id})
