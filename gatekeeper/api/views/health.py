from django.views.decorators.http import require_GET

from common.response import success_response


@require_GET
def health(request):
    """Shallow health check."""
    return success_response({"status": "OK"})
