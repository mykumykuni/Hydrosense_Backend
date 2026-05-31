from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, ProfileView, ChangePasswordView,
    UserListView, ApproveUserView, DeactivateUserView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    path('<int:pk>/approve/', ApproveUserView.as_view(), name='user-approve'),
    path('<int:pk>/deactivate/', DeactivateUserView.as_view(), name='user-deactivate'),
    path('', UserListView.as_view(), name='user-list'),
]
