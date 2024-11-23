from ..models import AdoptionNotice
from rest_framework import serializers




class AdoptionNoticeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AdoptionNotice
        fields = ['created_at', 'last_checked', "searching_since", "name", "description", "further_information", "group_only"]
