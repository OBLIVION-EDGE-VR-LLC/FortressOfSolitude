"""
DBA 1337_TECH, AUSTIN TEXAS © MAY 2021
Proof of Concept code, No liabilities or warranties expressed or implied.
"""

from django.contrib import admin

from .models import KEK, DEK, NeutronCore, NeutronMatterCollector, UserKeyPair


@admin.register(UserKeyPair)
class UserKeyPairAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    readonly_fields = ('encrypted_private_key', 'private_key_nonce', 'kek', 'dek')
    search_fields = ('user__email',)


admin.site.register(KEK)
admin.site.register(DEK)
admin.site.register(NeutronCore)
admin.site.register(NeutronMatterCollector)
