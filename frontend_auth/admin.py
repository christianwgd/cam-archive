from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import auth


User = auth.get_user_model()


class CustomUserAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CustomUserAdmin.list_display = [*list(UserAdmin.list_display), 'is_active']


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
