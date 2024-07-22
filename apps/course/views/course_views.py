from django.db.models import Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.filters import CourseFilter
from apps.course.models import Course, Enrollment
from apps.course.serializers.course_serializers import CourseListSerializer, CourseSerializer
from config.permissons import IsAdmin, IsAuth, IsAdminOrReadOnly

POPULAR_COURSES_COUNT = 3
MANUAL_PARAMETERS = [
    OpenApiParameter('search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Searching"),
    OpenApiParameter('category', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Category"),
    OpenApiParameter('teacher', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Teacher"),
    OpenApiParameter('enrolled', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Enrolled")
]


class CourseList(APIView):
    serializer_class = CourseListSerializer
    permission_classes = IsAdminOrReadOnly,

    @extend_schema(tags=['Course'], parameters=MANUAL_PARAMETERS, responses={200: serializer_class(many=True)})
    def get(self, request):
        courses = Course.objects.select_related('teacher', 'category').prefetch_related('sections')
        course_filter = CourseFilter(data=request.GET, request=request, queryset=courses)
        filtered_courses = course_filter.qs if course_filter.is_valid() else courses.none()
        serializer = self.serializer_class(filtered_courses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Course'], request=serializer_class(), responses={201: serializer_class()})
    def post(self, request):
        serializer = CourseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetail(APIView):
    serializer_class = CourseSerializer
    permission_classes = IsAdminOrReadOnly,

    @extend_schema(tags=['Course'], responses={200: serializer_class()})
    def get(self, request, course_id):
        course = self.get_course(course_id)
        serializer = self.serializer_class(course, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Course'], request=serializer_class(), responses={200: serializer_class()})
    def put(self, request, course_id):
        course = self.get_course(course_id)
        serializer = self.serializer_class(course, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['Course'], responses={200: OpenApiResponse(description='Course deleted')})
    def delete(self, request, course_id):
        course = self.get_course(course_id)
        course.delete()
        return Response({'message': 'Course deleted'}, status=status.HTTP_200_OK)

    def get_course(self, course_id):
        return get_object_or_404(Course, pk=course_id)


class CoursePopularList(APIView):
    serializer_class = CourseListSerializer
    permission_classes = IsAdminOrReadOnly,

    @extend_schema(tags=['Course'], responses={200: serializer_class(many=True)})
    def get(self, request):
        courses = Course.objects.select_related('teacher', 'category').prefetch_related('sections')
        popular_course = courses.annotate(count=Count('enrollments')).order_by('-count')[:POPULAR_COURSES_COUNT]
        course_filter = CourseFilter(request.GET, popular_course)
        filtered_courses = course_filter.qs if course_filter.is_valid() else courses.none()
        serializer = self.serializer_class(filtered_courses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseEnroll(APIView):

    @extend_schema(tags=['Enroll'], request=None, responses=OpenApiResponse(description='Enrolled'))
    def post(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course, id=course_id)
        Enrollment.objects.get_or_create(user=user, course=course)
        return Response({'message': 'Enrolled'}, status=status.HTTP_200_OK)

    def get_permissions(self):
        return IsAuth(),
