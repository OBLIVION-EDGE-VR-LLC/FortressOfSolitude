"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2021
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.contrib import admin

from .models import Tag, Tasking, Startup, NewsLink, UserFolder


admin.site.register(Tag)
admin.site.register(Tasking)
admin.site.register(Startup)
admin.site.register(NewsLink)


@admin.register(UserFolder)
class UserFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'parent', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name', 'owner__email')
    readonly_fields = ('kek', 'dek', 'dek_nonce')
