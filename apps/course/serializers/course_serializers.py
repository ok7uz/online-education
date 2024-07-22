from tokenize import group
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .color_serializers import ColorSerializer
from .course_part_serializers import CoursePartSerializer
from ..models import Color, CompletedLesson, Course, Category
from ...accounts.models import User
from ...accounts.serializers import TeacherSerializer


class CourseListSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    category_name = serializers.CharField(read_only=True, source='category.name')
    duration = serializers.IntegerField(read_only=True)
    enrolled = serializers.SerializerMethodField(read_only=True)
    completed_percentage = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    color1 = ColorSerializer(read_only=True)
    color2 = ColorSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'duration', 'category_name', 'teacher', 'image', 'video',
            'color1', 'color2', 'price', 'enrolled', 'completed_percentage', 'average_rating',
            'lessons_count', 'students_count', 'is_fragment',  'created_at',
        ]

    def get_enrolled(self, course) -> bool:
        user = self.context.get('request').user
        return user.is_authenticated and user.enrollments.filter(course=course).exists()

    @extend_schema_field(serializers.IntegerField(min_value=0, max_value=100))
    def get_completed_percentage(self, course):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return 0
        lessons_count = course.lessons_count
        completed_lessons_count = CompletedLesson.objects.filter(user=user, lesson__section__course=course).count()
        return completed_lessons_count * 100 // lessons_count if lessons_count > 0 else 0


class CourseSerializer(CourseListSerializer):
    teacher_id = serializers.UUIDField(write_only=True)
    category_id = serializers.UUIDField(write_only=True)
    color1_id = serializers.UUIDField(write_only=True, source='color1.id')
    color2_id = serializers.UUIDField(write_only=True, source='color2.id')

    color1 = ColorSerializer(read_only=True)
    color2 = ColorSerializer(read_only=True)

    average_rating = serializers.FloatField(min_value=0, max_value=5, read_only=True)
    parts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'category_name', 'category_id', 'teacher_id', 'teacher', 'color1', 'color2',
            'color1_id', 'color2_id', 'image', 'video', 'price_per_lesson', 'lessons_per_part', 'price', 'duration',
            'enrolled', 'average_rating', 'lessons_count', 'students_count', 'reviews_count',  'is_fragment',
            'completed_percentage', 'parts', 'created_at'
        ]

    @staticmethod
    def validate_category_id(value):
        get_object_or_404(Category, id=value)
        return value

    @staticmethod
    def validate_teacher_id(value):
        get_object_or_404(User, id=value, groups__name='teacher')
        return value

    @staticmethod
    def validate_video(value):
        content_type = value.content_type
        if not content_type.startswith('video'):
            raise serializers.ValidationError('The submitted file is not a video file')
        return value

    @extend_schema_field(CoursePartSerializer(many=True))
    def get_parts(self, value):
        parts = value.parts.all()
        return CoursePartSerializer(parts, many=True, context=self.context).data

    def create(self, validated_data):
        color1_data = validated_data.pop('color1')
        color2_data = validated_data.pop('color2')
        color1 = get_object_or_404(Color, **color1_data)
        color2 = get_object_or_404(Color, **color2_data)
        return Course.objects.create(
            color1=color1,
            color2=color2,
            **validated_data
        )

    def update(self, instance, validated_data):
        color1_data = validated_data.pop('color1', None)
        color2_data = validated_data.pop('color2', None)
        color1 = get_object_or_404(Color, **color1_data) if color1_data else instance.color1
        color2 = get_object_or_404(Color, **color2_data) if color2_data else instance.color2
        validated_data['color1'] = color1
        validated_data['color2'] = color2
        return super().update(instance, validated_data)
