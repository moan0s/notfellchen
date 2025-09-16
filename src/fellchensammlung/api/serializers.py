from ..models import Animal, RescueOrganization, AdoptionNotice, Species, Image, Location
from rest_framework import serializers
import math


class ImageSerializer(serializers.ModelSerializer):
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'image', 'alt_text', 'width', 'height']

    def get_width(self, obj):
        return obj.image.width

    def get_height(self, obj):
        return obj.image.height


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

    photos = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = AdoptionNotice
        fields = ['created_at', 'last_checked', "searching_since", "name", "description", "further_information",
                  "group_only", "location", "location_details", "organization", "photos", "adoption_notice_status"]


class AdoptionNoticeGeoJSONSerializer(serializers.ModelSerializer):
    species = serializers.SerializerMethodField()
    title = serializers.CharField(source='name')
    url = serializers.SerializerMethodField()
    location_hr = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image_alt = serializers.SerializerMethodField()

    class Meta:
        model = AdoptionNotice
        fields = ('id', 'species', 'title', 'description', 'url', 'location_hr', 'coordinates', 'image_url',
                  'image_alt')

    def get_species(self, obj):
        return "rat"

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_image_url(self, obj):
        photo = obj.get_photo()
        if photo is not None:
            return obj.get_photo().image.url
        return None

    def get_image_alt(self, obj):
        photo = obj.get_photo()
        if photo is not None:
            return obj.get_photo().alt_text
        return None

    def get_coordinates(self, obj):
        """
        Coordinates are randomly moved around real location, roughly in a circle. The object id is used as angle so that
        points are always displayed at the same location (as if they were a seed for a random function).

        It's not exactly a circle, because the earth is round.
        """
        if obj.location:
            longitude_addition = math.sin(obj.id) / 2000
            latitude_addition = math.cos(obj.id) / 2000
            return [obj.location.longitude + longitude_addition, obj.location.latitude + latitude_addition]
        return None

    def get_location_hr(self, obj):
        if obj.location:
            return f"{obj.location}"
        return None


class RescueOrgeGeoJSONSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    url = serializers.SerializerMethodField()
    location_hr = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = AdoptionNotice
        fields = ('id', 'name', 'description', 'url', 'location_hr', 'coordinates')

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_coordinates(self, obj):
        """
        Coordinates are randomly moved around real location, roughly in a circle. The object id is used as angle so that
        points are always displayed at the same location (as if they were a seed for a random function).

        It's not exactly a circle, because the earth is round.
        """
        if obj.location:
            return [obj.location.longitude, obj.location.latitude]
        return None

    def get_location_hr(self, obj):
        if obj.location.city:
            return f"{obj.location.city}"
        elif obj.location:
            return f"{obj.location}"
        return None


class AnimalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ["name", "date_of_birth", "description", "species", "sex", "adoption_notice"]


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
