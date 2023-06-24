from rest_framework.permissions import BasePermission


class Nobody(BasePermission):
    def has_permission(self, request, view):
        return False
