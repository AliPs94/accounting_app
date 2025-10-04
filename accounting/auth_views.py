from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Association, UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user and associate them with an organization"""
    data = request.data
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'association_id']
    for field in required_fields:
        if field not in data:
            return Response(
                {'error': f'{field} is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Check if user already exists
    if User.objects.filter(username=data['username']).exists():
        return Response(
            {'error': 'Username already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=data['email']).exists():
        return Response(
            {'error': 'Email already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if association exists
    try:
        association = Association.objects.get(id=data['association_id'])
    except Association.DoesNotExist:
        return Response(
            {'error': 'Association not found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    
    # Create user profile
    UserProfile.objects.create(
        user=user,
        association=association
    )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'association': association.name
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return JWT tokens"""
    data = request.data
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get user profile
    try:
        profile = UserProfile.objects.get(user=user)
        association = profile.association
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'association': association.name,
            'association_id': association.id
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['GET'])
def get_user_profile(request):
    """Get current user's profile information"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        association = profile.association
        
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'association': association.name,
                'association_id': association.id
            }
        })
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def switch_association(request):
    """Switch user's current association"""
    try:
        association_id = request.data.get('association_id')
        if not association_id:
            return Response(
                {'error': 'association_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if association exists
        try:
            association = Association.objects.get(id=association_id)
        except Association.DoesNotExist:
            return Response(
                {'error': 'Association not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'association': association}
        )
        
        if not created:
            # Update existing profile
            user_profile.association = association
            user_profile.save()
        
        return Response({
            'message': f'Successfully switched to {association.name}',
            'association': {
                'id': association.id,
                'name': association.name
            }
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

