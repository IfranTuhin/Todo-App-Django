from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
# pyrefly: ignore[missing-import]
from .models import TaskModel


def task_list(request):
    """
    Display task list with optional filtering and search,
    along with progress statistics.
    """
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('q', '').strip()

    tasks = TaskModel.objects.all()

    # Search query filtering
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Status filtering
    if filter_type == 'completed':
        tasks = tasks.filter(complated=True)
    elif filter_type == 'pending':
        tasks = tasks.filter(complated=False)

    # Calculate statistics across all user tasks
    all_tasks = TaskModel.objects.all()
    total_count = all_tasks.count()
    completed_count = all_tasks.filter(complated=True).count()
    pending_count = all_tasks.filter(complated=False).count()
    completion_percentage = int((completed_count / total_count * 100)) if total_count > 0 else 0

    context = {
        'tasks': tasks,
        'filter_type': filter_type,
        'search_query': search_query,
        'total_count': total_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'completion_percentage': completion_percentage,
    }
    return render(request, 'todo/task_list.html', context)


def task_create(request):
    """
    Create a new task with validation and flash notifications.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if title:
            TaskModel.objects.create(title=title, description=description)
            messages.success(request, f'Task "{title}" created successfully! 🚀')
            return redirect('todo:task_list')

        error = 'Title cannot be empty. Please enter a title for your task.'
        return render(request, 'todo/task_form.html', {
            'error': error,
            'title': title,
            'description': description,
            'action': 'create',
        })

    return render(request, 'todo/task_form.html', {'action': 'create'})


def task_edit(request, task_id):
    """
    Edit an existing task.
    """
    task = get_object_or_404(TaskModel, pk=task_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        complated = (request.POST.get('complated') == 'on' or request.POST.get('completed') == 'on')

        if title:
            task.title = title
            task.description = description
            task.complated = complated
            task.save()
            messages.success(request, f'Task "{title}" updated successfully! ✨')
            return redirect('todo:task_list')

        error = 'Title cannot be empty. Please enter a title for your task.'
        return render(request, 'todo/task_form.html', {
            'error': error,
            'task': task,
            'action': 'edit',
        })

    return render(request, 'todo/task_form.html', {
        'task': task,
        'action': 'edit',
    })


def task_delete(request, task_id):
    """
    Delete a task with confirmation support.
    """
    task = get_object_or_404(TaskModel, pk=task_id)

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.warning(request, f'Task "{task_title}" was deleted. 🗑️')
        return redirect('todo:task_list')

    return render(request, 'todo/task_delete.html', {'task': task})


def task_toggle(request, task_id):
    """
    Toggle completed status of a task. Supports AJAX and regular form/links.
    """
    task = get_object_or_404(TaskModel, pk=task_id)
    task.complated = not task.complated
    task.save()

    # Check for AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
        all_tasks = TaskModel.objects.all()
        total = all_tasks.count()
        completed = all_tasks.filter(complated=True).count()
        pending = total - completed
        percentage = int((completed / total * 100)) if total > 0 else 0

        return JsonResponse({
            'success': True,
            'id': task.id,
            'complated': task.complated,
            'completed': task.complated,
            'total_count': total,
            'completed_count': completed,
            'pending_count': pending,
            'completion_percentage': percentage,
            'message': f'Task status changed to {"completed" if task.complated else "pending"}.'
        })

    status_label = "completed" if task.complated else "active"
    messages.info(request, f'Task marked as {status_label}.')
    return redirect('todo:task_list')