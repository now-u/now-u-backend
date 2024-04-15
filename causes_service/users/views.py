from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import CausesUserSerializer, UserProfileSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

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

    def get_object(self):
        return self.request.user
