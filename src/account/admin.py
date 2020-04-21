from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models.users import User

admin.site.register(User, UserAdmin)
