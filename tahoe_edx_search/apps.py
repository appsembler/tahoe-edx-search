from django.apps import AppConfig


class TahoeEdXSearchApp(AppConfig):
    """
    Django and Open edX app configs.
    """
    name = 'tahoe_edx_search'
    label = 'tahoe_edx_search'
    verbose_name = 'A hack package to add Course Access Groups support for edx-search.'

    def ready(self):
        from .search_api_hack import override_course_discovery_search  # noqa: local import to avoid runtime errors
        override_course_discovery_search()
