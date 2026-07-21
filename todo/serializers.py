from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Task, TaskList


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class TaskListSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = TaskList
        fields = ['id', 'title', 'created_at', 'owner']


class TaskSerializer(serializers.ModelSerializer):
    task_list = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'deadline', 'priority', 'status', 'created_at', 'updated_at', 'task_list']
