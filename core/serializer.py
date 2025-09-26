from rest_framework import serializers

class generateResponseSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=8000,
        min_length=1,
        trim_whitespace=True
    )
    


