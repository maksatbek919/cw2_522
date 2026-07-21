from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TodoApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='secret123')
        self.client.force_authenticate(user=self.user)

    def test_register_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_list(self):
        response = self.client.post(reverse('task-list-list-create'), {'title': 'My list'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
