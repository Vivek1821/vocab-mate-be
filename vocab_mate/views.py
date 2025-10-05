from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from vocab_mate.generate_sentence import DailySentenceGenerator
from .models import Word, UserProgress
from .serializers import (
    DailySentenceSerializer,
    WordSerializer, 
    UserProgressSerializer, 
    UserSerializer,
    UserRegistrationSerializer
)


@extend_schema_view(
    get=extend_schema(
        summary="List all words",
        description="Retrieve a list of all words with optional filtering and search",
        parameters=[
            OpenApiParameter(
                name='difficulty_level',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by difficulty level (beginner, intermediate, advanced)'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in word and definition fields'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by: word, created_at, difficulty_level'
            ),
        ]
    ),
    post=extend_schema(
        summary="Create a new word",
        description="Add a new word to the vocabulary database"
    )
)
class WordListCreateView(generics.ListCreateAPIView):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['difficulty_level']
    search_fields = ['word', 'definition']
    ordering_fields = ['word', 'created_at', 'difficulty_level']


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a word",
        description="Get details of a specific word by ID"
    ),
    put=extend_schema(
        summary="Update a word",
        description="Update all fields of a specific word"
    ),
    patch=extend_schema(
        summary="Partially update a word",
        description="Update specific fields of a word"
    ),
    delete=extend_schema(
        summary="Delete a word",
        description="Remove a word from the database"
    )
)
class WordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    get=extend_schema(
        summary="List user progress",
        description="Get all learning progress for the authenticated user"
    ),
    post=extend_schema(
        summary="Create user progress",
        description="Add a new word to user's learning progress"
    )
)
class UserProgressListCreateView(generics.ListCreateAPIView):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve user progress",
        description="Get details of a specific learning progress entry"
    ),
    put=extend_schema(
        summary="Update user progress",
        description="Update all fields of a learning progress entry"
    ),
    patch=extend_schema(
        summary="Partially update user progress",
        description="Update specific fields of a learning progress entry"
    ),
    delete=extend_schema(
        summary="Delete user progress",
        description="Remove a learning progress entry"
    )
)
class UserProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user_id=self.request.user.id)


@extend_schema_view(
    post=extend_schema(
        summary="User Registration",
        description="Register a new user account",
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        }
    )
)
class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="User Login",
        description="Authenticate user and return JWT tokens",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,  # ✅ instead of embedding serializer class
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT
        }
    )
)
class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    summary="Get user profile",
    description="Retrieve the authenticated user's profile information",
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Get user statistics",
    description="Retrieve learning statistics for the authenticated user",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'total_words': {'type': 'integer'},
                'learned_words': {'type': 'integer'},
                'in_progress': {'type': 'integer'},
                'completion_percentage': {'type': 'number'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    total_words = Word.objects.count()
    learned_words = UserProgress.objects.filter(
        user_id=request.user.id, 
        is_learned=True
    ).count()
    in_progress = UserProgress.objects.filter(
        user_id=request.user.id, 
        is_learned=False
    ).count()
    
    return Response({
        'total_words': total_words,
        'learned_words': learned_words,
        'in_progress': in_progress,
        'completion_percentage': round((learned_words / total_words * 100), 2) if total_words > 0 else 0
    })

@extend_schema_view(
    get=extend_schema(
        summary="Generate daily sentences",
        description="Generate daily practice sentences for vocabulary learning",
        responses={200: OpenApiTypes.OBJECT}
    )
)
class GenerateDailySentencesView(APIView):
    permission_classes = [permissions.AllowAny]              # 👈 make it public
    authentication_classes = [] 
    serializer_class = DailySentenceSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        generator = DailySentenceGenerator()
        response = generator.generate_daily()
        # JsonResponse content is bytes, need to decode and parse
        import json
        content = json.loads(response.content.decode('utf-8'))
        return Response(content)
