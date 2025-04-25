from ..models import Animal, RescueOrganization, AdoptionNotice, Species, Image, Location
from rest_framework import serializers


class AdoptionNoticeSerializer(serializers.HyperlinkedModelSerializer):
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        required=False,
        allow_null=True
    )
    location_details = serializers.StringRelatedField(source='location', read_only=True)
    organization = serializers.PrimaryKeyRelatedField(
        queryset=RescueOrganization.objects.all(),
        required=False,
        allow_null=True
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=RescueOrganization.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = AdoptionNotice
        fields = ['created_at', 'last_checked', "searching_since", "name", "description", "further_information",
                  "group_only", "location", "location_details", "organization"]


class AnimalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ["name", "date_of_birth", "description", "species", "sex", "adoption_notice"]


class RescueOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescueOrganization
        fields = ["name", "location_string", "instagram", "facebook", "fediverse_profile", "email", "phone_number",
                  "website", "description", "external_object_identifier", "external_source_identifier"]


class AnimalGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = "__all__"


class RescueOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescueOrganization
        exclude = ["internal_comment", "allows_using_materials"]


class ImageCreateSerializer(serializers.ModelSerializer):
    @staticmethod
    def _animal_or_an(value):
        if not value in ["animal", "adoption_notice"]:
            raise serializers.ValidationError(
                'Set either animal or adoption_notice, depending on what type of object the image should be attached to.')

    attach_to_type = serializers.CharField(validators=[_animal_or_an])
    attach_to = serializers.IntegerField()

    class Meta:
        model = Image
        exclude = ["owner"]


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
