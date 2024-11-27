from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.list import ListView
from django.contrib.auth import login
from .models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

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
        
        # Pass search input back to the template for form rendering
        search_input = self.request.GET.get('search-area') or ''
        context['search_input'] = search_input
        
        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

    def get_queryset(self):
        # Restrict task details to tasks owned by the logged-in user
        return Task.objects.filter(user=self.request.user)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        # Restrict updates to tasks owned by the logged-in user
        return Task.objects.filter(user=self.request.user)

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        # Restrict deletions to tasks owned by the logged-in user
        return Task.objects.filter(user=self.request.user)

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']  # Exclude the 'user' field
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        # Assign the logged-in user as the task owner
        form.instance.user = self.request.user
        return super().form_valid(form)