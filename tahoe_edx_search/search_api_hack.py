"""
Module for Tahoe hacks for the edx-search repository.
"""

from logging import getLogger
from search import api as edx_search_api
from search import views as edx_search_views

log = getLogger(__name__)


def filter_results_with_has_access(results):
    """
    Filter CourseDiscovery search results via the edX Platform LMS `has_access` function.

    This is a hack function that should be refactored into the LMS.
    See RED-637.
    """
    from lms.djangoapps.courseware import access
    from crum import get_current_request
    from opaque_keys.edx.keys import CourseKey
    from xmodule.modulestore.django import modulestore

    module_store = modulestore()
    user = get_current_request().user

    for result in results["results"]:
        course_key = CourseKey.from_string(result['data']['id'])
        course = module_store.get_course(course_key, depth=0)
        if not (course and access.has_access(user, 'see_in_catalog', course)):
            result["data"] = None

    # Count and remove the results that has no access
    access_denied_count = len([r for r in results["results"] if r["data"] is None])
    results["access_denied_count"] = access_denied_count
    results["results"] = [r for r in results["results"] if r["data"] is not None]

    # Hack: Naively reduce the facet numbers by the access denied results
    # This is not the smartest hack, and customers could report issues
    # The solution is most likely to just remove the facet numbers
    results["total"] = max(0, results["total"] - access_denied_count)
    for _name, facet in list(results["facets"].items()):
        facet["other"] = max(0, facet.get("other", 0) - access_denied_count)
        facet["terms"] = {
            term: max(0, count - access_denied_count)
            for term, count in list(facet["terms"].items())
            # Remove the facet terms that has no results
            if max(0, count - access_denied_count)
        }
    return results


def override_course_discovery_search():
    func_path = 'course_discovery_search'
    upstream_course_discovery_search = getattr(edx_search_api, func_path)
    if upstream_course_discovery_search.__name__ != func_path:
        raise Exception('course_discovery_search: Should not be overridden twice')

    def tahoe_hacked_course_discovery_search(*args, **kwargs):
        """
        A modified function of upstream edx-search `search.api.course_discovery_search` to support CAG.
        """
        results = upstream_course_discovery_search
        return filter_results_with_has_access(results)

    for module_ in [edx_search_api, edx_search_views]:
        current_function = getattr(module_, func_path)
        if current_function.__name__ == 'course_discovery_search':
            setattr(module_, func_path, tahoe_hacked_course_discovery_search)
            log.warning('Hack: Override course_discovery_search for `has_access`/`cag` support in %s', module_)
