from django.contrib.auth.models import Group
from django.db.models import Prefetch
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.accounts.serializers import UserSerializer, TeacherSerializer, RegisterSerializer
from apps.accounts.models import User
from apps.course.models import Course
from config.permissons import IsAdminOrReadOnly, IsAuth


class ProfileAPIView(APIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuth,)

    @extend_schema(
        responses={200: UserSerializer},
        tags=['Profile'],
        description='Get profile info'
    )
    def get(self, request):
        serializer = self.serializer_class(request.user, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=['Profile'],
        description='Update profile info'
    )
    def put(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        tags=['Profile'],
        description='Delete profile'
    )
    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileAPIView(APIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={200: UserSerializer},
        tags=['User'],
        description='Get profile info'
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = self.serializer_class(user, context={'request': request})
        return Response(serializer.data)


class TeacherListAPIView(APIView):
    serializer_class = TeacherSerializer
    permission_classes = IsAdminOrReadOnly,

    @extend_schema(
        responses={200: TeacherSerializer},
        tags=['Teacher'],
        description='Get teacher list'
    )
    def get(self, request):
        users = User.objects.filter(groups__name='teacher').prefetch_related(
            Prefetch('courses', queryset=Course.objects.all())
        ).prefetch_related(
            Prefetch('enrollments__course__teacher', queryset=User.objects.all())
        ).order_by('created_at')
        serializer = self.serializer_class(users, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        request=RegisterSerializer,
        responses={201: TeacherSerializer},
        tags=['Teacher'],
        description='Create new teacher'
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            teacher_group, _ = Group.objects.get_or_create(name='teacher')
            serializer.instance.groups.add(teacher_group)
            serializer.instance.save()
            teacher_serializer = self.serializer_class(serializer.instance, context={'request': request})
            return Response(teacher_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
