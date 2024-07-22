from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.course.models import Color, CompletedLesson, Course, Section, Lesson, Video, Enrollment, Category, CoursePart


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'courses_count')
    fields = ('name', 'courses_count', 'created_at')
    readonly_fields = ('courses_count', 'created_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'average_rating', 'duration', 'lessons_count')
    list_filter = ('category',)
    fields = (
        'title', 'teacher', 'category', ('color1', 'color1_bar'), ('color2', 'color2_bar'),
        'description', 'image', 'lessons_per_part', 'price_per_lesson', 
        'average_rating', 'duration', 'lessons_count', 'created_at'
    )
    readonly_fields = ('average_rating', 'duration', 'created_at', 'lessons_count', 'color1_bar', 'color2_bar')
    search_fields = ('title',)

    def color1_bar(self, course):
        hex_code = course.color1.hex_code
        return mark_safe(f'<div style="background: {hex_code}; padding: 10px; border: 1px solid black"></div>')
    
    def color2_bar(self, course):
        hex_code = course.color2.hex_code
        return mark_safe(f'<div style="background: {hex_code}; padding: 10px; border: 1px solid black"></div>')
    
    color1_bar.short_description = ''
    color2_bar.short_description = ''


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration', 'lessons_count')
    list_filter = ('course',)
    fields = ('title', 'course', 'duration', 'lessons_count', 'created_at')
    readonly_fields = ('created_at', 'duration', 'lessons_count', 'order')
    ordering = ('course__title', 'order')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'section', 'order', 'duration')
    list_filter = ('section',)
    fields = ('title', 'section', 'content', 'duration', 'created_at')
    readonly_fields = ('course', 'created_at', 'order')
    ordering = ('section__course__title', 'section__order', 'order')

    @staticmethod
    def course(lesson):
        return lesson.section.course


@admin.register(CompletedLesson)
class CompletedLessonAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')
    list_filter = ('user',)
    fields = ('user', 'lesson', 'completed_at')
    readonly_fields = ('completed_at',)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'video_480p')
    list_filter = ('lesson',)
    fields = ('lesson', 'video_1080p', 'video_720p', 'video_480p', 'video_360p', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    list_filter = ('user', 'course')
    fields = ('user', 'course', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code', 'color_bar')
    fields = ('name', ('hex_code', 'color_bar'))
    readonly_fields = ('color_bar',)

    def color_bar(self, color):
        return mark_safe(f'<div style="background: {color.hex_code}; padding: 10px; border: 1px solid black"></div>')
    
    color_bar.short_description = ''


@admin.register(CoursePart)
class CoursePartAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'course', 'order')
    list_filter = ('course',)
    fields = ('course', 'order')
    readonly_fields = ('order',)
