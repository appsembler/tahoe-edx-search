from django.apps import AppConfig


class SiteConfigApp(AppConfig):
    """
    Django and Open edX app configs.
    """
    name = 'tahoe_search_cag_support'
    label = 'tahoe_search_cag_support'
    verbose_name = 'A hack package to add Course Access Groups support for edx-search.'

    def ready(self):
        from .search_api_hack import override_course_discovery_search
        override_course_discovery_search()

