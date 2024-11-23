from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from fellchensammlung.models import AdoptionNotice, Animal, Log, TrustLevel
from fellchensammlung.tasks import add_adoption_notice_location
from .serializers import AdoptionNoticeSerializer


class AdoptionNoticeApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer_context = {
            'request': request,
        }
        adoption_notices = AdoptionNotice.objects.all()
        serializer = AdoptionNoticeSerializer(adoption_notices, many=True, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        API view to add an adoption notice.b
        """
        serializer = AdoptionNoticeSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        adoption_notice = serializer.save(owner=request.user)

        # Add the location
        add_adoption_notice_location.delay_on_commit(adoption_notice.pk)

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
