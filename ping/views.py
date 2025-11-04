from django.http import JsonResponse
import os
import sys
import django
from datetime import datetime


# Create your views here.
def ping(request):
    # Get request information
    request_info = {
        "message": "pong",
        "timestamp": datetime.now().isoformat(),
        # Request details
        "request": {
            "method": request.method,
            "path": request.path,
            "full_path": request.get_full_path(),
            "scheme": request.scheme,
            "is_secure": request.is_secure(),
            "content_type": request.content_type,
            "encoding": request.encoding,
        },
        # Headers
        "headers": dict(request.headers),
        # GET parameters
        "get_params": dict(request.GET),
        # POST data (if any)
        "post_data": dict(request.POST) if request.method == "POST" else None,
        # User information
        "user": {
            "is_authenticated": request.user.is_authenticated,
            "username": request.user.username
            if request.user.is_authenticated
            else None,
            "is_staff": request.user.is_staff
            if request.user.is_authenticated
            else None,
            "is_superuser": request.user.is_superuser
            if request.user.is_authenticated
            else None,
        },
        # Server information
        "server": {
            "django_version": django.get_version(),
            "python_version": sys.version,
            "platform": sys.platform,
            "server_name": os.environ.get(
                "COMPUTERNAME", os.environ.get("HOSTNAME", "Unknown")
            ),
            "working_directory": os.getcwd(),
        },
        # Session data
        "session": {
            "session_key": request.session.session_key,
            "session_data": dict(request.session)
            if hasattr(request, "session")
            else None,
        },
        # Meta information
        "meta": {
            "remote_addr": request.META.get("REMOTE_ADDR"),
            "remote_host": request.META.get("REMOTE_HOST"),
            "server_name": request.META.get("SERVER_NAME"),
            "server_port": request.META.get("SERVER_PORT"),
            "http_user_agent": request.META.get("HTTP_USER_AGENT"),
            "http_accept": request.META.get("HTTP_ACCEPT"),
            "http_accept_language": request.META.get("HTTP_ACCEPT_LANGUAGE"),
            "http_accept_encoding": request.META.get("HTTP_ACCEPT_ENCODING"),
            "content_length": request.META.get("CONTENT_LENGTH"),
            "query_string": request.META.get("QUERY_STRING"),
            "request_method": request.META.get("REQUEST_METHOD"),
            "path_info": request.META.get("PATH_INFO"),
            "script_name": request.META.get("SCRIPT_NAME"),
        },
    }

    return JsonResponse(request_info)
