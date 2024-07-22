import django_filters.rest_framework as filters

from apps.course.models import Course


class CourseFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='title', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    teacher = filters.CharFilter(field_name='teacher__username', lookup_expr='icontains')
    enrolled = filters.BooleanFilter(method='filter_enrolled')
    # popular = filters.BooleanFilter(field_name='popular', lookup_expr='exact')

    class Meta:
        model = Course
        fields = ['search', 'category', 'teacher', 'enrolled']

    def filter_enrolled(self, queryset, _, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        match value:
            case True:
                return queryset.filter(enrollments__user=user)
            case False:
                return queryset.exclude(enrollments__user=user)
            case _:
                return queryset
