from django.test import TestCase, Client
from django.urls import reverse
# pyrefly: ignore[missing-import]
from .models import TaskModel


class TodoAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.task1 = TaskModel.objects.create(
            title="First Demo Task",
            description="Details about first demo task",
            complated=False
        )
        self.task2 = TaskModel.objects.create(
            title="Second Completed Task",
            description="Already done task",
            complated=True
        )

    def test_task_list_view(self):
        url = reverse('todo:task_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_list.html')
        self.assertContains(response, "First Demo Task")
        self.assertContains(response, "Second Completed Task")
        self.assertEqual(response.context['total_count'], 2)
        self.assertEqual(response.context['completed_count'], 1)
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(response.context['completion_percentage'], 50)

    def test_task_filter(self):
        url = reverse('todo:task_list') + '?filter=completed'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Second Completed Task")
        self.assertNotContains(response, "First Demo Task")

    def test_task_search(self):
        url = reverse('todo:task_list') + '?q=First'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First Demo Task")
        self.assertNotContains(response, "Second Completed Task")

    def test_task_create_get(self):
        url = reverse('todo:task_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_form.html')

    def test_task_create_post(self):
        url = reverse('todo:task_create')
        response = self.client.post(url, {
            'title': 'Brand New Task',
            'description': 'Automated test task description'
        })
        self.assertRedirects(response, reverse('todo:task_list'))
        self.assertTrue(TaskModel.objects.filter(title='Brand New Task').exists())

    def test_task_create_empty_title_fails(self):
        url = reverse('todo:task_create')
        response = self.client.post(url, {'title': '   ', 'description': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Title cannot be empty')

    def test_task_edit(self):
        url = reverse('todo:task_edit', args=[self.task1.id])
        response = self.client.post(url, {
            'title': 'First Demo Task Updated',
            'description': 'Updated details',
            'complated': 'on'
        })
        self.assertRedirects(response, reverse('todo:task_list'))
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'First Demo Task Updated')
        self.assertTrue(self.task1.complated)

    def test_task_toggle_redirect(self):
        url = reverse('todo:task_toggle', args=[self.task1.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('todo:task_list'))
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.complated)

    def test_task_toggle_ajax(self):
        url = reverse('todo:task_toggle', args=[self.task1.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertTrue(json_data['completed'])

    def test_task_delete(self):
        url = reverse('todo:task_delete', args=[self.task1.id])
        # GET renders confirmation
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_delete.html')

        # POST performs delete
        post_response = self.client.post(url)
        self.assertRedirects(post_response, reverse('todo:task_list'))
        self.assertFalse(TaskModel.objects.filter(id=self.task1.id).exists())
