from django.contrib import admin
from .models import Word, UserProgress


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'difficulty_level', 'created_at']
    list_filter = ['difficulty_level', 'created_at']
    search_fields = ['word', 'definition']
    ordering = ['word']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'word_id', 'is_learned', 'times_reviewed', 'last_reviewed']
    list_filter = ['is_learned', 'last_reviewed']
    search_fields = ['user_id', 'word_id']
    ordering = ['-last_reviewed']
