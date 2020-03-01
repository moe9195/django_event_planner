from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    message = "Only the organizer has access!"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
