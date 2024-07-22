from rest_framework import serializers

from apps.course.models import Color


class ColorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']

    @staticmethod
    def validate_hex_code(value):
        valid = value.startswith('#') and len(value) == 7
        if not valid:
            raise serializers.ValidationError('hex code is not valid (must be like #a1b2c3)')
        return value
