from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from ..models import AdoptionNotice
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

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.data.get('name'),
            "searching_since": request.data.get('searching_since'),
            "description": request.data.get('description'),
            "organization": request.data.get('organization'),
            "further_information": request.data.get('further_information'),
            "location_string": request.data.get('location_string'),
            "group_only": request.data.get('group_only'),
            "owner": request.data.get('owner')
        }
        serializer = AdoptionNoticeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
