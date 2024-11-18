from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, Application
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token
from datetime import timedelta
from django.utils import timezone
from employeeAPI.models import Employee
from django.contrib.auth import logout

@api_view(['POST'])
@permission_classes([AllowAny]) #allows unauthenticated users to generate their token
def get_token_for_manager(request):
    manager_id = request.data.get('managerID')

    # validate that manager_id is int
    if not manager_id or not isinstance(manager_id, int):
        return Response({"error": "manager_id is required and must be an integer."}, status=400)

    # verify existence in DB
    try:
        manager = Employee.objects.get(employeeid=manager_id, employmentstatus='active', type='Manager')
    except Employee.DoesNotExist:
        return Response({"error": "Invalid or inactive manager ID."}, status=404)

    # using the User table that django makes, check if the given id is already associated with a user entry
    user, created = User.objects.get_or_create(username=f'manager_{manager_id}')

    # ensure there is an OAuth application to issue the token. uses a seperate django built table
    application, app_created = Application.objects.get_or_create(
        name="Manager App",
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_PASSWORD,
        user=user
    )

    # access token generation
    expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = AccessToken.objects.create(
        user=user,
        application=application,
        token=generate_token(),
        expires=expires,
        scope="read write"
    )

    return Response({
        "access_token": access_token.token,
        "expires_in": oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        "token_type": "Bearer",
        "scope": access_token.scope
    }, status=200)

@api_view(['POST'])
def logout_user(request):
    if hasattr(request, 'auth') and request.auth: #should have an attached access token
        try:
            access_token = AccessToken.objects.get(token=request.auth.token)
            access_token.expires = timezone.now() # Set the expiration of the token to now to invalidate it
            access_token.save()
            return Response({"message": "Logged out successfully and token invalidated."}, status=200)
        except AccessToken.DoesNotExist:
            return Response({"error": "Access token not found."}, status=400)
    else:
        return Response({"error": "No token provided in the request."}, status=400)
    
    
    