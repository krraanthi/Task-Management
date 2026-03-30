from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Project, Task

# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'tasks/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'tasks/project_detail.html'

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
        return super().form_valid(form)

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
