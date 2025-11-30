from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from rest_framework.generics import ListAPIView

from fellchensammlung.api.serializers import LocationSerializer, AdoptionNoticeGeoJSONSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from fellchensammlung.models import Log, TrustLevel, Location, AdoptionNoticeStatusChoices
from fellchensammlung.tasks import post_adoption_notice_save, post_rescue_org_save
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated

from .renderers import GeoJSONRenderer
from .serializers import (
    AnimalGetSerializer,
    AnimalCreateSerializer,
    RescueOrgeGeoJSONSerializer,
    AdoptionNoticeSerializer,
    ImageCreateSerializer,
    SpeciesSerializer, RescueOrganizationSerializer,
)
from fellchensammlung.models import Animal, RescueOrganization, AdoptionNotice, Species, Image
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter


class AdoptionNoticeApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            {
                'name': 'id',
                'required': False,
                'description': 'ID of the adoption notice to retrieve.',
                'type': int
            },
        ],
        responses={200: AdoptionNoticeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve adoption notices with their related animals and images.
        """
        adoption_notice_id = kwargs.get("id")
        if adoption_notice_id:
            try:
                adoption_notice = AdoptionNotice.objects.get(pk=adoption_notice_id)
                serializer = AdoptionNoticeSerializer(adoption_notice, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except AdoptionNotice.DoesNotExist:
                return Response({"error": "Adoption notice not found."}, status=status.HTTP_404_NOT_FOUND)
        adoption_notices = AdoptionNotice.objects.all()
        serializer = AdoptionNoticeSerializer(adoption_notices, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @extend_schema(
        request=AdoptionNoticeSerializer,
        responses={201: 'Adoption notice created successfully!'}
    )
    def post(self, request, *args, **kwargs):
        """
        API view to add an adoption notice.
        """
        serializer = AdoptionNoticeSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        adoption_notice = serializer.save(owner=request.user_to_notify)

        # Add the location
        post_adoption_notice_save.delay_on_commit(adoption_notice.pk)

        # Only set active when user has trust level moderator or higher
        if request.user_to_notify.trust_level >= TrustLevel.MODERATOR:
            adoption_notice.adoption_notice_status = AdoptionNoticeStatusChoices.Active.SEARCHING
        else:
            adoption_notice.adoption_notice_status = AdoptionNoticeStatusChoices.AwaitingAction.WAITING_FOR_REVIEW

        # Log the action
        Log.objects.create(
            user=request.user_to_notify,
            action="add_adoption_notice",
            text=f"{request.user_to_notify} added adoption notice {adoption_notice.pk} via API",
        )

        # Return success response with new adoption notice details
        return Response(
            {"message": "Adoption notice created successfully!", "id": adoption_notice.pk},
            status=status.HTTP_201_CREATED,
        )


class AnimalApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=AnimalGetSerializer
    )
    def get(self, request, *args, **kwargs):
        """
        Get list of animals or a specific animal by ID.
        """
        animal_id = kwargs.get("id")
        if animal_id:
            try:
                animal = Animal.objects.get(pk=animal_id)
                serializer = AnimalGetSerializer(animal, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Animal.DoesNotExist:
                return Response({"error": "Animal not found."}, status=status.HTTP_404_NOT_FOUND)
        animals = Animal.objects.all()
        serializer = AnimalGetSerializer(animals, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @extend_schema(
        request=AnimalCreateSerializer,
        responses={201: inline_serializer(
            name='Animal',
            fields={
                'id': serializers.IntegerField(),
                "message": serializers.Field()}),
            400: "json"}
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Create a new animal.
        """
        serializer = AnimalCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            animal = serializer.save(owner=request.user_to_notify)
            return Response(
                {"message": "Animal created successfully!", "id": animal.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RescueOrganizationApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            {
                'name': 'id',
                'required': False,
                'description': 'ID of the rescue organization to retrieve.',
                'type': int
            },
            {
                'name': 'trusted',
                'required': False,
                'description': 'Filter by trusted status (true/false).',
                'type': bool
            },
            {
                'name': 'external_object_identifier',
                'required': False,
                'description': 'Filter by external object identifier. Use "None" to filter for an empty field',
                'type': str
            },
            {
                'name': 'external_source_identifier',
                'required': False,
                'description': 'Filter by external source identifier. Use "None" to filter for an empty field',
                'type': str
            },
            {
                'name': 'search',
                'required': False,
                'description': 'Search by organization name or location name/city.',
                'type': str
            },
        ],
        responses={200: RescueOrganizationSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """
        Get list of rescue organizations or a specific organization by ID or get a list with available filters for
        - external_object_identifier
        - external_source_identifier
        """
        org_id = request.query_params.get("id")
        external_object_identifier = request.query_params.get("external_object_identifier")
        external_source_identifier = request.query_params.get("external_source_identifier")
        search_query = request.query_params.get("search")

        if org_id:
            try:
                organization = RescueOrganization.objects.get(pk=org_id)
                serializer = RescueOrganizationSerializer(organization, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except RescueOrganization.DoesNotExist:
                return Response({"error": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

        organizations = RescueOrganization.objects.all()

        if external_object_identifier:
            if external_object_identifier == "None":
                external_object_identifier = None
            organizations = organizations.filter(external_object_identifier=external_object_identifier)

        if external_source_identifier:
            if external_source_identifier == "None":
                external_source_identifier = None
            organizations = organizations.filter(external_source_identifier=external_source_identifier)
        if search_query:
            organizations = organizations.filter(
                Q(name__icontains=search_query) |
                Q(location_string__icontains=search_query) |
                Q(location__name__icontains=search_query) |
                Q(location__city__icontains=search_query)
            )
        if organizations.count() == 0:
            return Response({"error": "No organizations found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RescueOrganizationSerializer(organizations, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @extend_schema(
        request=RescueOrganizationSerializer,
        responses={201: 'Rescue organization created successfully!'}
    )
    def post(self, request, *args, **kwargs):
        """
        Create or update a rescue organization.
        """
        serializer = RescueOrganizationSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            rescue_org = serializer.save()
            if rescue_org.location is None:
                # Add the location
                post_rescue_org_save.delay_on_commit(rescue_org.pk)
            return Response(
                {"message": "Rescue organization created successfully!", "id": rescue_org.id},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @extend_schema(
        request=RescueOrganizationSerializer,
        responses={200: 'Rescue organization updated successfully!'}
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially update a rescue organization.
        """
        org_id = request.data.get("id")
        if not org_id:
            return Response({"error": "ID is required for updating."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = RescueOrganization.objects.get(pk=org_id)
        except RescueOrganization.DoesNotExist:
            return Response({"error": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RescueOrganizationSerializer(organization, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Rescue organization updated successfully!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddImageApiView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    @extend_schema(
        request=ImageCreateSerializer,
        responses={201: 'Image added successfully!'}
    )
    def post(self, request, *args, **kwargs):
        """
        Add an image to an animal or adoption notice.
        """
        serializer = ImageCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            if serializer.validated_data["attach_to_type"] == "animal":
                object_to_attach_to = Animal.objects.get(id=serializer.validated_data["attach_to"])
            elif serializer.validated_data["attach_to_type"] == "adoption_notice":
                object_to_attach_to = AdoptionNotice.objects.get(id=serializer.validated_data["attach_to"])
            else:
                raise ValueError("Unknown attach_to_type given, should not happen. Check serializer")
            serializer.validated_data.pop('attach_to_type', None)
            serializer.validated_data.pop('attach_to', None)
            image = serializer.save(owner=request.user_to_notify)
            object_to_attach_to.photos.add(image)
            return Response(
                {"message": "Image added successfully!", "id": image.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpeciesApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: SpeciesSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of species.
        """
        species = Species.objects.all()
        serializer = SpeciesSerializer(species, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class LocationApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            {
                'name': 'id',
                'required': False,
                'description': 'ID of the location to retrieve.',
                'type': int
            },
        ],
        responses={200: LocationSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a location
        """
        location_id = kwargs.get("id")
        if location_id:
            try:
                location = Location.objects.get(pk=location_id)
                serializer = LocationSerializer(location, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Location.DoesNotExist:
                return Response({"error": "Location not found."}, status=status.HTTP_404_NOT_FOUND)
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @extend_schema(
        request=LocationSerializer,
        responses={201: 'Location created successfully!'}
    )
    def post(self, request, *args, **kwargs):
        """
        API view to add a location
        """
        serializer = LocationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        location = serializer.save()

        # Log the action
        Log.objects.create(
            user=request.user,
            action="add_location",
            text=f"{request.user} added adoption notice {location.pk} via API",
        )

        # Return success response with new adoption notice details
        return Response(
            {"message": "Location created successfully!", "id": location.pk},
            status=status.HTTP_201_CREATED,
        )


class AdoptionNoticeGeoJSONView(ListAPIView):
    queryset = AdoptionNotice.objects.select_related('location').filter(location__isnull=False).filter(
        adoption_notice_status__in=AdoptionNoticeStatusChoices.Active.values)
    serializer_class = AdoptionNoticeGeoJSONSerializer
    renderer_classes = [GeoJSONRenderer]


class RescueOrgGeoJSONView(ListAPIView):
    queryset = RescueOrganization.objects.select_related('location').filter(location__isnull=False)
    serializer_class = RescueOrgeGeoJSONSerializer
    renderer_classes = [GeoJSONRenderer]


class AdoptionNoticePerOrgApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='id',
                required=False,
                description='ID of the rescue organization from which to retrieve adoption notices.',
                type=OpenApiTypes.INT
            ),
            OpenApiParameter(
                name='in_hierarchy',
                type=OpenApiTypes.BOOL,
                required=False,
                description='Show all Adoption Notices in hierarchy.',
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                required=False,
                description='Show all Adoption Notices in a certain status. Comma separated list of values e.g. '
                            '"active,closed"',
            ),
        ],
        responses={200: AdoptionNoticeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve adoption notices with their related animals and images.
        """
        org_id = kwargs.get("id")
        in_hierarchy = request.query_params.get("in_hierarchy")
        an_status = request.query_params.get("status")
        try:
            org = RescueOrganization.objects.get(id=org_id)
        except RescueOrganization.DoesNotExist:
            return Response({"error": "Rescue Organization notice not found."}, status=status.HTTP_404_NOT_FOUND)
        if in_hierarchy:
            adoption_notices = org.adoption_notices_in_hierarchy
        else:
            adoption_notices = AdoptionNotice.objects.filter(organization=org)
        if an_status:
            status_list = an_status.lower().strip().split(",")
            temporary_an_storage = []
            if "active" in status_list:
                active_ans = [adoption_notice for adoption_notice in adoption_notices if
                              adoption_notice.adoption_notice_status in AdoptionNoticeStatusChoices.Active.values]
                temporary_an_storage.extend(active_ans)
            if "closed" in status_list:
                closed_ans = [adoption_notice for adoption_notice in adoption_notices if
                              adoption_notice.adoption_notice_status in AdoptionNoticeStatusChoices.Closed.values]
                temporary_an_storage.extend(closed_ans)
            if "disabled" in status_list:
                disabled_ans = [adoption_notice for adoption_notice in adoption_notices if
                                adoption_notice.adoption_notice_status in AdoptionNoticeStatusChoices.Disabled.values]
                temporary_an_storage.extend(disabled_ans)
            if "awaiting_action" in status_list:
                awaiting_action_ans = [adoption_notice for adoption_notice in adoption_notices if
                                       adoption_notice.adoption_notice_status in AdoptionNoticeStatusChoices.AwaitingAction.values]
                temporary_an_storage.extend(awaiting_action_ans)
            adoption_notices = temporary_an_storage
        serializer = AdoptionNoticeSerializer(adoption_notices, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


def index(request):
    return redirect(reverse("swagger-ui"))
