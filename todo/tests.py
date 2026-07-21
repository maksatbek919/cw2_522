from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task, TaskList


class TodoApiTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='tester', password='secret123')
        self.client.force_authenticate(user=self.user)

    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_create_task_list(self):
        response = self.client.post(reverse('task-list-list-create'), {'title': 'My list'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_user_model_is_custom(self):
        self.assertEqual(settings.AUTH_USER_MODEL, 'todo.User')

    def test_tasks_can_be_filtered_by_status(self):
        task_list = TaskList.objects.create(title='Filtered list', owner=self.user)
        Task.objects.create(title='First task', status='done', task_list=task_list)
        Task.objects.create(title='Second task', status='new', task_list=task_list)

        response = self.client.get(reverse('task-list-task-list', kwargs={'task_list_id': task_list.id}) + '?status=done')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'First task')
