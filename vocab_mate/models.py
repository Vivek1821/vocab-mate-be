from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models


class Word(djongo_models.Model):
    word = djongo_models.CharField(max_length=100, unique=True)
    definition = djongo_models.TextField()
    pronunciation = djongo_models.CharField(max_length=100, blank=True)
    example_sentence = djongo_models.TextField(blank=True)
    difficulty_level = djongo_models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    tags = djongo_models.TextField(blank=True, default='')  # Store as comma-separated string
    synonyms = djongo_models.TextField(blank=True, default='')  # Store as comma-separated string
    antonyms = djongo_models.TextField(blank=True, default='')  # Store as comma-separated string
    created_at = djongo_models.DateTimeField(auto_now_add=True)
    updated_at = djongo_models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ['word']
        db_table = 'words'


class UserProgress(djongo_models.Model):
    user_id = djongo_models.IntegerField()  # Reference to Django User ID
    word_id = djongo_models.ObjectIdField()  # Reference to Word ObjectId
    is_learned = djongo_models.BooleanField(default=False)
    times_reviewed = djongo_models.PositiveIntegerField(default=0)
    last_reviewed = djongo_models.DateTimeField(auto_now=True)
    created_at = djongo_models.DateTimeField(auto_now_add=True)
    # Additional MongoDB-specific fields
    learning_streak = djongo_models.PositiveIntegerField(default=0)
    mastery_score = djongo_models.FloatField(default=0.0)  # 0.0 to 1.0
    review_schedule = djongo_models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_reviewed']
        db_table = 'user_progress'
        indexes = [
            djongo_models.Index(fields=['user_id', 'word_id']),
            djongo_models.Index(fields=['user_id', 'is_learned']),
            djongo_models.Index(fields=['review_schedule']),
        ]


class UserProfile(djongo_models.Model):
    user_id = djongo_models.IntegerField(unique=True)  # Reference to Django User ID
    total_words_learned = djongo_models.PositiveIntegerField(default=0)
    current_streak = djongo_models.PositiveIntegerField(default=0)
    longest_streak = djongo_models.PositiveIntegerField(default=0)
    preferred_difficulty = djongo_models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    daily_goal = djongo_models.PositiveIntegerField(default=10)
    learning_preferences = djongo_models.TextField(blank=True, default='')  # Store as JSON string
    created_at = djongo_models.DateTimeField(auto_now_add=True)
    updated_at = djongo_models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

class DailySentence(models.Model):
    date = models.DateField(auto_now_add=True)
    hindi = models.TextField()
    english = models.TextField()
    german = models.TextField(blank=True, null=True)
    hash = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f"{self.hindi} → {self.english} → {self.german}"
