from django.http import HttpResponseRedirect
from django.urls import reverse


class ApiBrowserRedirectMiddleware:
    """Redirect browser navigations away from raw /api/* endpoints to web UI."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_redirect(request):
            return HttpResponseRedirect(reverse("genealogy:person-list"))
        return self.get_response(request)

    @staticmethod
    def _should_redirect(request) -> bool:
        if request.method != "GET":
            return False
        if not request.path.startswith("/api/"):
            return False
        if request.path.startswith("/api/auth/") or request.path == "/api/schema/":
            return False
        if request.GET.get("format") == "json":
            return False

        accept = request.META.get("HTTP_ACCEPT", "")
        wants_html = "text/html" in accept
        has_auth = bool(request.META.get("HTTP_AUTHORIZATION"))
        return wants_html and not has_auth
