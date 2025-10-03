from __future__ import annotations

from django.http import HttpRequest


def theme(request: HttpRequest) -> dict[str, str]:
    user = getattr(request, "user", None)
    if user and user.is_authenticated and user.theme_preference:
        theme_preference = user.theme_preference
    else:
        theme_preference = request.session.get("theme", "system")
    return {"theme_preference": theme_preference}
