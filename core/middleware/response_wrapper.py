import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class ResponseWrapperMiddleware(MiddlewareMixin):
    """
    Middleware to wrap every response in a consistent JSON structure:
    - success: true/false
    - response: actual data
    - error: { message, details }
    """

    def process_response(self, request, response):
        try:
            # Handle Django Rest Framework or JsonResponse responses
            if isinstance(response, JsonResponse):
                data = json.loads(response.content.decode())
            elif hasattr(response, 'data'):
                data = response.data
            else:
                # Non-JSON responses (HTML, file downloads, etc.)
                return response

            status_code = getattr(response, 'status_code', 200)
            success = 200 <= status_code < 300

            # Construct consistent structure
            if success:
                formatted = {
                    "success": True,
                    "response": data
                }
            else:
                # Extract simple error message if possible
                message = ""
                details = ""
                if isinstance(data, dict):
                    message = data.get("detail") or data.get("message") or "An error occurred"
                    details = data
                else:
                    message = str(data)
                    details = None

                formatted = {
                    "success": False,
                    "response": data,
                    "error": {
                        "message": message,
                        "details": details
                    }
                }

            # Return standardized JsonResponse
            return JsonResponse(formatted, status=status_code, safe=False)

        except Exception as e:
            # In case our middleware itself crashes
            return JsonResponse({
                "success": False,
                "response": None,
                "error": {
                    "message": "Internal Server Error",
                    "details": str(e)
                }
            }, status=500)

