from rest_framework import serializers

class PredictInputSerializer(serializers.Serializer):
    orbital_period = serializers.FloatField()
    transit_duration = serializers.FloatField()
    planet_radius = serializers.FloatField()
    stellar_temp = serializers.FloatField(required=False, default=0)

class PredictOutputSerializer(serializers.Serializer):
    prediction = serializers.CharField()
    confidence = serializers.FloatField()
