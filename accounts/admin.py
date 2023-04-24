from django.contrib import admin
from accounts.models import AWTUser


class AWTUserAdmin(admin.ModelAdmin):
    fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "is_superuser",
        "last_login",
        "date_joined",
        "saved_station",
        "saved_query",
        "is_upgraded",
        "upgrade_uuid",
    ]
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "last_login",
        "date_joined",
        "is_staff",
        "is_active",
        "is_upgraded",
    ]
    list_display_links = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_upgraded",
    ]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_upgraded",
        "upgrade_uuid",
    ]


admin.site.register(AWTUser, AWTUserAdmin)
