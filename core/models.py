from django.conf import settings
from django.db import models


class Task(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.order}. {self.title}"


class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    current_step = models.PositiveIntegerField(default=0)
    total_steps = models.PositiveIntegerField(default=0)
    last_score = models.IntegerField(null=True, blank=True)
    stars = models.PositiveSmallIntegerField(default=0)  # total stars (legacy)
    easy_stars   = models.PositiveSmallIntegerField(default=0)
    medium_stars = models.PositiveSmallIntegerField(default=0)
    hard_stars   = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "task")


class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    notes = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)




class Classroom(models.Model):
    """A teacher's class. Students join with the join_code."""
    teacher    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="classrooms")
    name       = models.CharField(max_length=80)
    join_code  = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.join_code})"

class UserProfile(models.Model):
    """Stores total stars (shop currency) and role for each user."""
    ROLE_CHOICES = [("student", "Student"), ("teacher", "Teacher")]
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_stars = models.PositiveIntegerField(default=0)
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    classroom   = models.ForeignKey("Classroom", null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="students")

    @property
    def is_teacher(self):
        return self.role == "teacher"

    def __str__(self):
        return f"{self.user.username} ({self.role}) — {self.total_stars} stars"


class ShopItem(models.Model):
    """Items available in the shop (ready for future use)."""
    TASK_CHOICES = [('ribbon','Ribbon'),('cookie','Cookie'),('pizza','Pizza'),('general','General')]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    task_tag = models.CharField(max_length=20, choices=TASK_CHOICES, default='general')
    theme_key = models.CharField(max_length=50, blank=True, default='')  # e.g. 'jungle', 'colour_red'
    cost = models.PositiveIntegerField(default=1)
    emoji = models.CharField(max_length=10, default="🎁")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.emoji} {self.name} ({self.cost} stars)"


class UserShopItem(models.Model):
    """Tracks which items a user has purchased."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "item")
