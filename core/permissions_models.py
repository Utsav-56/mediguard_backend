from rest_framework.permissions import BasePermission


class EveryoneAllowed(BasePermission):
    """
    Permission class that allows unrestricted access to any user,
    "authenticated or not."
    """

    def has_permission(self, request, view):
        return True


class OnlyLoggedUser(BasePermission):
    """
    Permission class that allows access only to authenticated users.

    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminUser(BasePermission):
    """
    Permission class that allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
