from rest_framework.permissions import BasePermission


class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser and request.user.is_staff)


class IsAuthorPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

