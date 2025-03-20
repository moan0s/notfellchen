from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from fellchensammlung.models import AdoptionNotice, Animal, Log, TrustLevel
from fellchensammlung.tasks import post_adoption_notice_save, post_rescue_org_save
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    AnimalGetSerializer,
    AnimalCreateSerializer,
    RescueOrganizationSerializer,
    AdoptionNoticeSerializer,
    ImageCreateSerializer,
    SpeciesSerializer, RescueOrgSerializer,
)
from fellchensammlung.models import Animal, RescueOrganization, AdoptionNotice, Species, Image
from drf_spectacular.utils import extend_schema


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

        adoption_notice = serializer.save(owner=request.user)

        # Add the location
        post_adoption_notice_save.delay_on_commit(adoption_notice.pk)

        # Only set active when user has trust level moderator or higher
        if request.user.trust_level >= TrustLevel.MODERATOR:
            adoption_notice.set_active()
        else:
            adoption_notice.set_unchecked()

        # Log the action
        Log.objects.create(
            user=request.user,
            action="add_adoption_notice",
            text=f"{request.user} added adoption notice {adoption_notice.pk} via API",
        )

        # Return success response with new adoption notice details
        return Response(
            {"message": "Adoption notice created successfully!", "id": adoption_notice.pk},
            status=status.HTTP_201_CREATED,
        )


class AnimalApiView(APIView):
    permission_classes = [IsAuthenticated]

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
    def post(self, request, *args, **kwargs):
        """
        Create a new animal.
        """
        serializer = AnimalCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            animal = serializer.save(owner=request.user)
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
        ],
        responses={200: RescueOrganizationSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """
        Get list of rescue organizations or a specific organization by ID.
        """
        org_id = kwargs.get("id")
        if org_id:
            try:
                organization = RescueOrganization.objects.get(pk=org_id)
                serializer = RescueOrganizationSerializer(organization, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except RescueOrganization.DoesNotExist:
                return Response({"error": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)
        organizations = RescueOrganization.objects.all()
        serializer = RescueOrganizationSerializer(organizations, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @extend_schema(
        request=RescueOrgSerializer,  # Document the request body
        responses={201: 'Rescue organization created/updated successfully!'}
    )
    def post(self, request, *args, **kwargs):
        """
        Create or update a rescue organization.
        """
        serializer = RescueOrgSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            rescue_org = serializer.save()
            # Add the location
            post_rescue_org_save.delay_on_commit(rescue_org.pk)
            return Response(
                {"message": "Rescue organization created/updated successfully!", "id": rescue_org.id},
                status=status.HTTP_201_CREATED,
            )


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
            image = serializer.save(owner=request.user)
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
