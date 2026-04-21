from django.contrib import admin
from .models import Task, Progress, Attempt, UserProfile, Classroom, ShopItem, UserShopItem


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ("order", "title", "slug", "is_available")
    list_editable = ("is_available",)
    ordering      = ("order",)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display  = ("user", "task", "easy_stars", "medium_stars", "hard_stars",
                     "completed", "last_score", "updated_at")
    list_filter   = ("completed", "task")
    search_fields = ("user__username",)
    ordering      = ("-updated_at",)
    list_editable = ("easy_stars", "medium_stars", "hard_stars")

    def save_model(self, request, obj, form, change):
        obj.stars = obj.easy_stars + obj.medium_stars + obj.hard_stars
        super().save_model(request, obj, form, change)
        profile = obj.user.userprofile
        total = sum(
            p.easy_stars + p.medium_stars + p.hard_stars
            for p in Progress.objects.filter(user=obj.user)
        )
        profile.total_stars = total
        profile.save()


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display  = ("user", "task", "score", "created_at")
    list_filter   = ("task",)
    search_fields = ("user__username",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "role", "classroom", "total_stars")
    list_filter   = ("role",)
    search_fields = ("user__username",)
    list_editable = ("total_stars",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display  = ("name", "join_code", "teacher", "student_count", "created_at")
    search_fields = ("name", "join_code", "teacher__username")

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = "Students"


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display  = ("emoji", "name", "task_tag", "theme_key", "cost", "is_available")
    list_editable = ("is_available", "cost")
    list_filter   = ("task_tag", "is_available")


@admin.register(UserShopItem)
class UserShopItemAdmin(admin.ModelAdmin):
    list_display  = ("user", "item", "purchased_at")
    list_filter   = ("item__task_tag",)
    search_fields = ("user__username",)
