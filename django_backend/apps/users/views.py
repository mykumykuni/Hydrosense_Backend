from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer
from .models import UserProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Allow updating profile sub-fields in the same request
        profile_data = request.data.pop('profile', None)
        response = super().update(request, *args, **kwargs)
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            from .serializers import UserProfileSerializer
            ps = UserProfileSerializer(profile, data=profile_data, partial=True)
            ps.is_valid(raise_exception=True)
            ps.save()
        return response


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Incorrect password.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data['new_password'])
        # Revoke all existing JWTs after a password change
        user.revoked_since = timezone.now()
        user.save(update_fields=['password', 'revoked_since'])
        return Response({'detail': 'Password updated. Please log in again.'})


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['role', 'status']
    search_fields = ['email', 'profile__display_name']


class ApproveUserView(APIView):
    """Admin approves a pending operator account."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.status != 'pending':
            return Response({'detail': 'User is not pending.'}, status=status.HTTP_400_BAD_REQUEST)

        user.status = 'active'
        user.approved_at = timezone.now()
        user.save(update_fields=['status', 'approved_at'])
        return Response(UserSerializer(user).data)


class DeactivateUserView(APIView):
    """Admin deactivates an active account and revokes all JWTs."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        user.status = 'inactive'
        user.deactivated_at = now
        user.revoked_since = now
        user.save(update_fields=['status', 'deactivated_at', 'revoked_since'])
        return Response(UserSerializer(user).data)
