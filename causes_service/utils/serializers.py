from users.models import User

def get_user_from_context(context: dict) -> User | None:
    request = context.get("request")
    if request and hasattr(request, "user"):
        return request.user
    return None
