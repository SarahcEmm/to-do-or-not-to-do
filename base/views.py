from django.shortcuts import render, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Task


# Custom LoginView
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, 'You have successfully logged in!')
        return reverse_lazy('tasks')


# Custom logout for aleret
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('login')


# Register Page for user sign-up
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


# Task List
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_queryset(self):
        # Fetch tasks for the logged-in user
        user = self.request.user
        queryset = Task.objects.filter(user=user)

        # Apply search filter if 'search-area' parameter is present
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            queryset = queryset.filter(title__icontains=search_input)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Search area
        search_input = self.request.GET.get('search-area') or ''
        context['search_input'] = search_input

        # Number of incomplete tasks
        incomplete_tasks = Task.objects.filter(
            user=self.request.user,
            complete=False
        )
        context['count'] = incomplete_tasks.count()

        return context


# Task detail
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

    def get_queryset(self):
        # make sure only one user
        return Task.objects.filter(user=self.request.user)


# Task modification
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        # Restrict updates to tasks owned by the logged-in user
        return Task.objects.filter(user=self.request.user)

# Task Delete
class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, 'You have successfully deleted the task!')
        return super().get_success_url()


# Task creation
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        # Assign user
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)