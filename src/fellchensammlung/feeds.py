from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from django.urls import reverse
from django.utils.xmlutils import SimplerXMLGenerator

from .models import AdoptionNotice


class FormattedFeed(Rss201rev2Feed):
    """

    """
    content_type = "text/xml; charset=utf-8"
    def write(self, outfile, encoding):
        handler = SimplerXMLGenerator(outfile, encoding, short_empty_elements=True)
        handler.startDocument()
        handler._write('<?xml-stylesheet href="/static/rss.xsl" type="text/xsl"?>')
        handler.startElement("rss", self.rss_attributes())
        handler.startElement("channel", self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        self.endChannelElement(handler)
        handler.endElement("rss")


class LatestAdoptionNoticesFeed(Feed):
    feed_type = FormattedFeed
    title = "Notfellchen"
    link = "/rss/"
    description = "Updates zu neuen Vermittlungen."

    def items(self):
        return AdoptionNotice.objects.order_by("-created_at")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description
