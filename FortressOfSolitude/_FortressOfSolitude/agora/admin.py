"""
DBA 1337_TECH, AUSTIN TEXAS
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.contrib import admin

from .models import AgoraProfile, Category, Topic, Reply


@admin.register(AgoraProfile)
class AgoraProfileAdmin(admin.ModelAdmin):
    list_display = ('handle', 'user', 'created_at')
    search_fields = ('handle', 'user__email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'pub_date', 'is_pinned', 'is_locked', 'view_count')
    list_filter = ('category', 'is_pinned', 'is_locked')
    search_fields = ('title', 'author__handle')
    readonly_fields = ('data_dek', 'data_kek', 'result_nonce_text')


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'pub_date', 'parent')
    list_filter = ('topic__category',)
    search_fields = ('author__handle', 'topic__title')
    readonly_fields = ('data_dek', 'data_kek', 'result_nonce_text')
