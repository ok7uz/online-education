from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.course.models import Section, CompletedLesson, CoursePart
from apps.course.serializers.lesson_serializers import LessonListSerializer


class CoursePartSectionsSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField(read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    completed_percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Section
        fields = ('id', 'title', 'completed_percentage', 'duration', 'order', 'created_at', 'lessons_count', 'lessons')

    @extend_schema_field(LessonListSerializer(many=True))
    def get_lessons(self, section):
        lessons = self.context.get('lessons')
        return LessonListSerializer(lessons.filter(section=section), many=True, context=self.context).data

    def get_lessons_count(self, section) -> int:
        lessons = self.context.get('lessons')
        return lessons.filter(section=section).count()

    @extend_schema_field(serializers.IntegerField(min_value=0, max_value=100))
    def get_completed_percentage(self, section):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return 0
        lessons_count = section.lessons_count
        completed_lessons_count = CompletedLesson.objects.filter(user=user, lesson__section=section).count()
        return completed_lessons_count * 100 // lessons_count if lessons_count > 0 else 0


class CoursePartSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CoursePart
        fields = ('id', 'order', 'price', 'lessons_count', 'sections')

    @staticmethod
    def get_lessons_count(part) -> int:
        return part.lessons.count()

    def get_price(self, part) -> int:
        return self.get_lessons_count(part) * part.course.price_per_lesson

    @extend_schema_field(CoursePartSectionsSerializer(many=True))
    def get_sections(self, part):
        lessons = part.lessons.all()
        self.context['lessons'] = lessons
        section_ids = lessons.values_list('section', flat=True).distinct()
        sections = Section.objects.filter(id__in=section_ids)
        return CoursePartSectionsSerializer(sections, many=True, context=self.context).data
