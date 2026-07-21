from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, mixins, serializers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Task, TaskList
from .pagination import CustomPagination
from .permissions import IsOwner
from .serializers import TaskListSerializer, TaskSerializer, UserCreateSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description='Register a new user account')
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class TaskListListCreateView(generics.GenericAPIView,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = CustomPagination

    def get_queryset(self):
        return TaskList.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(operation_description='List and create task lists for the current user')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description='Create a new task list for the current user')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TaskListDetailView(generics.GenericAPIView,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return TaskList.objects.all()

    def get_object(self):
        obj = get_object_or_404(TaskList, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(operation_description='Retrieve a specific task list')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description='Update a task list')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description='Partially update a task list')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description='Delete a task list')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'deadline']
    search_fields = ['title']
    ordering_fields = ['deadline', 'created_at']

    def get_queryset(self):
        queryset = Task.objects.filter(task_list__owner=self.request.user)
        task_list_id = self.kwargs.get('task_list_id')
        if task_list_id:
            queryset = queryset.filter(task_list_id=task_list_id)
        return queryset

    def get_object(self):
        obj = get_object_or_404(Task, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        task_list_id = self.kwargs.get('task_list_id') or self.request.data.get('task_list')
        if not task_list_id:
            raise serializers.ValidationError({'task_list': 'This field is required.'})

        task_list = get_object_or_404(TaskList, pk=task_list_id, owner=self.request.user)
        serializer.save(task_list=task_list)


class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(operation_description='Obtain JWT access and refresh tokens')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(operation_description='Refresh an existing JWT token')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
