from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer

from .serializers import CausesUserSerializer, UserProfileGetSerializer, UserProfileUpdateSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.request.method in ["PUT", "POST", "PATCH"]:
            return UserProfileUpdateSerializer
        return UserProfileGetSerializer

    def get_object(self):
        return self.request.user

# TODO Potentially move this (and the serializer + methods to the causes app)
class CausesUserView(generics.RetrieveUpdateAPIView):
    """
    View for information about the users interactions with causes resources
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CausesUserSerializer

    def get_object(self):
        return self.request.user

class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileGetSerializer

    def get_object(self):
        return self.request.user
