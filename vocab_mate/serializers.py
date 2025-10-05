from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Word, UserProgress, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class UserProgressSerializer(serializers.ModelSerializer):
    word = WordSerializer(read_only=True)
    word_id = serializers.CharField(write_only=True)  # ObjectId as string

    class Meta:
        model = UserProgress
        fields = [
            'word', 'word_id', 'is_learned', 'times_reviewed', 
            'last_reviewed', 'created_at', 'learning_streak', 
            'mastery_score', 'review_schedule'
        ]
        read_only_fields = ['last_reviewed', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'total_words_learned', 'current_streak', 'longest_streak',
            'preferred_difficulty', 'daily_goal', 'learning_preferences',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Create user profile in MongoDB
        UserProfile.objects.create(
            user_id=user.id,
            preferred_difficulty='beginner',
            daily_goal=10
        )
        return user


class DailySentenceSerializer(serializers.Serializer):
    hindi = serializers.CharField()
    english = serializers.CharField()
    german = serializers.CharField(required=False, allow_blank=True)