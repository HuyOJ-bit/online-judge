from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class UserAdmin(DjangoUserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "email", "is_staff", "date_joined",
                    "submission_count", "solved_count")

    @admin.display(description="Submissions")
    def submission_count(self, obj):
        return obj.submissions.count()

    @admin.display(description="Solved")
    def solved_count(self, obj):
        return obj.submissions.filter(verdict="AC").values("problem").distinct().count()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "institution", "created_at")
    search_fields = ("user__username", "full_name", "institution")
