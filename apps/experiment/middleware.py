import logging

from .models import NavigationLog
from .services import ExperimentSession

logger = logging.getLogger(__name__)

URL_PAGE_TYPE = {
    "topic_list": "topic",
    "keyword_list": "keyword",
    "question_list": "keyword_item",
}


class NavigationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ExperimentSession(request.session).initialize()
        response = self.get_response(request)

        if (
            request.method == "GET"
            and response.status_code == 200
            and request.session.get("task_active")
        ):
            try:
                self._log(request)
            except Exception as exc:
                logger.warning("NavigationMiddleware: log failed: %s", exc)

        return response

    def _log(self, request):
        match = request.resolver_match
        if not match:
            return
        page_type = URL_PAGE_TYPE.get(match.url_name)
        if not page_type:
            return
        if not request.session.session_key:
            request.session.create()
        NavigationLog.objects.create(
            session_key=request.session.session_key,
            task_id=request.session.get("task_id"),
            page_type=page_type,
            page_id=getattr(request, "_nav_page_id", None),
            page_name=getattr(request, "_nav_page_name", match.url_name),
        )
