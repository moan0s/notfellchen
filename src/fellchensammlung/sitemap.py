from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import AdoptionNotice, RescueOrganization, ImportantLocation, Animal


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["index", "search", "map", "about", "rescue-organizations", "buying", "imprint", "terms-of-service",
                "privacy"]

    def location(self, item):
        return reverse(item)


class AdoptionNoticeSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return AdoptionNotice.get_active_ANs()

    def lastmod(self, obj):
        return obj.updated_at


class RescueOrganizationSitemap(Sitemap):
    priority = 0.3
    changefreq = "weekly"

    def items(self):
        return RescueOrganization.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class SearchSitemap(Sitemap):
    priority = 0.5
    chanfreq = "daily"

    def items(self):
        return ImportantLocation.objects.all()
