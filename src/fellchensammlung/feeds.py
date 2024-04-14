from django.contrib.syndication.views import Feed

from django.urls import reverse
from .models import AdoptionNotice


class LatestAdoptionNoticesFeed(Feed):
    title = "Nptfellchen"
    link = "/rss/"
    description = "Updates zu neuen Vermittlungen."

    def items(self):
        return AdoptionNotice.objects.order_by("-created_at")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

