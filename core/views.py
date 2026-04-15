import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Task, Progress, UserProfile, ShopItem, UserShopItem, Classroom


def _seed_tasks():
    for slug, title, order in [
        ("task-10-ribbon", "Ribbon and Bows", 10),
        ("task-12-cookie", "Cookie Share",    12),
        ("task-14-pizza",  "Pizza Division",  14),
    ]:
        Task.objects.get_or_create(slug=slug, defaults={"title": title, "order": order, "is_available": True})

def _seed_shop_items():
    """Auto-create shop items if the table is empty."""
    if ShopItem.objects.exists():
        return
    items = [
        # Ribbon colour packs
        dict(name="Red Ribbon",      task_tag="ribbon", theme_key="colour_red",
             emoji="🔴", cost=2,  description="Turn the ribbon bold crimson red. Classic and striking!"),
        dict(name="Blue Ribbon",     task_tag="ribbon", theme_key="colour_blue",
             emoji="🔵", cost=2,  description="Change the ribbon to a cool ocean blue."),
        dict(name="Rainbow Ribbon",  task_tag="ribbon", theme_key="colour_rainbow",
             emoji="🌈", cost=4,  description="A gorgeous fading rainbow ribbon — red, orange, yellow, green, blue, purple!"),
        dict(name="Glitter Gold",    task_tag="ribbon", theme_key="colour_glitter",
             emoji="✨", cost=5,  description="Sparkling golden glitter ribbon. Fancy!"),
        # Cookie character packs
        dict(name="Jungle Pack",     task_tag="cookie", theme_key="jungle",
             emoji="🌴", cost=5,
             description="Mouse → 🐯 Tiger\nWolf → 🐒 Monkey\nHuman → 🦜 Parrot\nLion → 🐘 Elephant"),
        dict(name="Ocean Pack",      task_tag="cookie", theme_key="ocean",
             emoji="🌊", cost=5,
             description="Mouse → 🦀 Crab\nWolf → 🐬 Dolphin\nHuman → 🦈 Shark\nLion → 🐋 Whale"),
        dict(name="Space Pack",      task_tag="cookie", theme_key="space",
             emoji="🚀", cost=7,
             description="Mouse → 👾 Alien\nWolf → 🛸 UFO\nHuman → 🤖 Robot\nLion → 🪐 Planet"),
        # Pizza theme packs
        dict(name="Halloween Pack",  task_tag="pizza",  theme_key="halloween",
             emoji="🎃", cost=5,
             description="🎃 Ghost · 🧟 Zombie · 🧛 Vampire · 🧙 Witch\nOrange & black pizza!"),
        dict(name="Christmas Pack",  task_tag="pizza",  theme_key="christmas",
             emoji="🎄", cost=5,
             description="🎅 Santa · 🤶 Mrs Claus · 🦌 Reindeer · ⛄ Snowman\nRed & green Christmas pizza!"),
    ]
    for d in items:
        ShopItem.objects.create(**d, is_available=True)



def _get_profile(user):
    p, _ = UserProfile.objects.get_or_create(user=user)
    return p


def _owned_themes(user, task_tag):
    """Return list of theme_keys the user owns for a given task."""
    owned_ids = UserShopItem.objects.filter(user=user).values_list("item_id", flat=True)
    return list(ShopItem.objects.filter(id__in=owned_ids, task_tag=task_tag)
                .values_list("theme_key", flat=True))


@login_required
def tasks(request):
    _seed_tasks()
    profile  = _get_profile(request.user)
    # Teachers should use the dashboard, not the student homepage
    if profile.is_teacher:
        return redirect("core:teacher_dashboard")
    playable = Task.objects.filter(is_available=True).order_by("order")
    items = []
    for task in playable:
        prog, _ = Progress.objects.get_or_create(user=request.user, task=task)
        diffs_done = sum([
            1 if prog.easy_stars   > 0 else 0,
            1 if prog.medium_stars > 0 else 0,
            1 if prog.hard_stars   > 0 else 0,
        ])
        items.append({
            "task":         task,
            "completed":    prog.completed,
            "easy_stars":   prog.easy_stars,
            "medium_stars": prog.medium_stars,
            "hard_stars":   prog.hard_stars,
            "diffs_done":   diffs_done,
        })
    # Count completions per difficulty across all tasks (max = tasks * 3 = 9)
    total_diffs     = playable.count() * 3   # 3 tasks × 3 difficulties = 9
    completed_diffs = sum(
        (1 if i["easy_stars"]   > 0 else 0) +
        (1 if i["medium_stars"] > 0 else 0) +
        (1 if i["hard_stars"]   > 0 else 0)
        for i in items
    )
    percent = round(completed_diffs / total_diffs * 100) if total_diffs else 0
    return render(request, "core/tasks.html", {
        "items": items,
        "completed_count": completed_diffs,
        "total": total_diffs,
        "percent": percent,
        "total_stars": profile.total_stars,
    })


@login_required
def task_detail(request, slug):
    _seed_tasks()
    task = get_object_or_404(Task, slug=slug)
    prog, _ = Progress.objects.get_or_create(user=request.user, task=task)
    tag_map = {"task-10-ribbon": "ribbon", "task-12-cookie": "cookie", "task-14-pizza": "pizza"}
    tag = tag_map.get(slug, "")
    owned = _owned_themes(request.user, tag)
    templates = {
        "task-10-ribbon": "core/ribbon_task.html",
        "task-12-cookie": "core/cookie_task.html",
        "task-14-pizza":  "core/pizza_task.html",
    }
    return render(request, templates.get(slug, "core/task_placeholder.html"), {
        "task": task, "progress": prog,
        "owned_themes": json.dumps(owned),   # passed as JSON to JS
    })


@login_required
@require_POST
def save_progress(request, slug):
    task = get_object_or_404(Task, slug=slug)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"ok": False, "error": "bad json"}, status=400)

    prog, _ = Progress.objects.get_or_create(user=request.user, task=task)
    diff     = data.get("difficulty", "easy")
    new_stars = max(1, min(int(data.get("stars", 1)), 6 if diff == "hard" else 3))
    completed = bool(data.get("completed", False))

    if data.get("score") is not None:
        score = int(data["score"])
        if prog.last_score is None or score > prog.last_score:
            prog.last_score = score
    if completed:
        prog.completed = True

    profile = _get_profile(request.user)
    if diff == "easy":
        if new_stars > prog.easy_stars:
            profile.total_stars += new_stars - prog.easy_stars
            prog.easy_stars = new_stars
    elif diff == "medium":
        if new_stars > prog.medium_stars:
            profile.total_stars += new_stars - prog.medium_stars
            prog.medium_stars = new_stars
    else:
        if new_stars > prog.hard_stars:
            profile.total_stars += new_stars - prog.hard_stars
            prog.hard_stars = new_stars

    prog.stars = prog.easy_stars + prog.medium_stars + prog.hard_stars
    profile.save()
    prog.save()
    return JsonResponse({
        "ok": True,
        "easy_stars":   prog.easy_stars,
        "medium_stars": prog.medium_stars,
        "hard_stars":   prog.hard_stars,
        "total_stars":  profile.total_stars,
    })


@login_required
def shop(request):
    _seed_tasks()
    _seed_shop_items()
    profile   = _get_profile(request.user)
    items     = ShopItem.objects.filter(is_available=True).order_by("task_tag", "cost")
    owned_ids = set(UserShopItem.objects.filter(user=request.user).values_list("item_id", flat=True))
    # Group by task_tag
    grouped = {}
    for item in items:
        grouped.setdefault(item.task_tag, []).append({"item": item, "owned": item.id in owned_ids})
    return render(request, "core/shop.html", {
        "grouped": grouped,
        "total_stars": profile.total_stars,
    })


@login_required
@require_POST
def buy_item(request, item_id):
    item    = get_object_or_404(ShopItem, id=item_id, is_available=True)
    profile = _get_profile(request.user)
    if UserShopItem.objects.filter(user=request.user, item=item).exists():
        return JsonResponse({"ok": False, "error": "Already owned"})
    if profile.total_stars < item.cost:
        return JsonResponse({"ok": False, "error": "Not enough stars"})
    profile.total_stars -= item.cost
    profile.save()
    UserShopItem.objects.create(user=request.user, item=item)
    return JsonResponse({"ok": True, "remaining_stars": profile.total_stars,
                         "theme_key": item.theme_key, "task_tag": item.task_tag})


def register(request):
    from django.conf import settings as django_settings
    TEACHER_PIN = getattr(django_settings, "TEACHER_PIN", "2004")

    error = None
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        role = request.POST.get("role", "student")
        pin  = request.POST.get("teacher_pin", "").strip()

        if role == "teacher" and pin != TEACHER_PIN:
            error = "Incorrect teacher PIN. Please try again."
        elif form.is_valid():
            user = form.save()
            profile = _get_profile(user)
            profile.role = role
            # Link student to classroom if code provided
            if role == "student":
                class_code = request.POST.get("class_code", "").strip().upper()
                if class_code:
                    try:
                        classroom = Classroom.objects.get(join_code=class_code)
                        profile.classroom = classroom
                    except Classroom.DoesNotExist:
                        # Delete the user we just created and show error
                        user.delete()
                        error = f"Classroom code '{class_code}' not found. Ask your teacher for the correct code."
                        return render(request, "registration/register.html",
                                      {"form": UserCreationForm(), "error": error,
                                       "class_code": class_code})
            profile.save()
            login(request, user)
            if role == "teacher":
                messages.success(request, "Teacher account created! Welcome to the dashboard.")
                return redirect("core:teacher_dashboard")
            else:
                messages.success(request, "Account created! Welcome to Maths Mayhem 🎉")
                return redirect("core:tasks")
        # form invalid — fall through to re-render
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form, "error": error})


# ── TEACHER VIEWS ──────────────────────────────────────────────────────────

def teacher_required(view_fn):
    """Decorator: user must be logged in AND have teacher role."""
    from functools import wraps
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect("login")
        profile = _get_profile(request.user)
        if not profile.is_teacher:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Teacher accounts only.")
        return view_fn(request, *args, **kwargs)
    return wrapper


@teacher_required
def teacher_dashboard(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    _seed_tasks()

    # Teacher's classrooms
    classrooms = Classroom.objects.filter(teacher=request.user).order_by("created_at")
    active_class_id = request.GET.get("class")
    active_classroom = None
    if active_class_id:
        try:
            active_classroom = classrooms.get(id=int(active_class_id))
        except (Classroom.DoesNotExist, ValueError):
            pass
    if not active_classroom and classrooms.exists():
        active_classroom = classrooms.first()

    tasks = Task.objects.filter(is_available=True).order_by("order")

    # Only show students in THIS teacher's active classroom
    if active_classroom:
        student_profiles = UserProfile.objects.filter(
            role="student", classroom=active_classroom
        ).select_related("user")
    else:
        student_profiles = UserProfile.objects.none()

    students = []
    for profile in student_profiles.order_by("user__username"):
        u = profile.user
        task_data = []
        total_diffs = 0
        completed_diffs = 0
        for task in tasks:
            prog = Progress.objects.filter(user=u, task=task).first()
            e  = prog.easy_stars   if prog else 0
            me = prog.medium_stars if prog else 0
            h  = prog.hard_stars   if prog else 0
            total_diffs     += 3
            completed_diffs += (1 if e>0 else 0) + (1 if me>0 else 0) + (1 if h>0 else 0)
            task_data.append({
                "task": task,
                "easy_stars":   e,
                "medium_stars": me,
                "hard_stars":   h,
                "done_count":   (1 if e>0 else 0) + (1 if me>0 else 0) + (1 if h>0 else 0),
            })
        students.append({
            "user":             u,
            "profile":          profile,
            "task_data":        task_data,
            "completed_diffs":  completed_diffs,
            "total_diffs":      total_diffs,
            "percent":          round(completed_diffs / total_diffs * 100) if total_diffs else 0,
            "last_active":      Progress.objects.filter(user=u).order_by("-updated_at").values_list("updated_at", flat=True).first(),
        })

    return render(request, "core/teacher_dashboard.html", {
        "students":        students,
        "tasks":           tasks,
        "total_students":  len(students),
        "classrooms":      classrooms,
        "active_classroom": active_classroom,
    })


@teacher_required
def student_detail(request, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    _seed_tasks()
    student = get_object_or_404(User, id=user_id)
    profile = _get_profile(student)
    if profile.is_teacher:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("That is a teacher account.")
    # Make sure this student is in one of this teacher's classrooms
    teacher_class_ids = Classroom.objects.filter(teacher=request.user).values_list("id", flat=True)
    if profile.classroom_id not in list(teacher_class_ids):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("This student is not in your classroom.")

    tasks = Task.objects.filter(is_available=True).order_by("order")
    task_data = []
    for task in tasks:
        prog = Progress.objects.filter(user=student, task=task).first()
        e  = prog.easy_stars   if prog else 0
        me = prog.medium_stars if prog else 0
        h  = prog.hard_stars   if prog else 0
        task_data.append({
            "task":          task,
            "easy_stars":    e,
            "medium_stars":  me,
            "hard_stars":    h,
            "last_score":    prog.last_score if prog else None,
            "updated_at":    prog.updated_at if prog else None,
        })

    # Recent attempts (last 20)
    recent = (Progress.objects
              .filter(user=student)
              .select_related("task")
              .order_by("-updated_at")[:10])

    return render(request, "core/student_detail.html", {
        "student":    student,
        "profile":    profile,
        "task_data":  task_data,
        "recent":     recent,
    })


@teacher_required
def create_classroom(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("join_code", "").strip().upper()
        if not name:
            return render(request, "core/create_classroom.html",
                          {"error": "Please enter a class name."})
        if not code:
            return render(request, "core/create_classroom.html",
                          {"error": "Please enter a join code."})
        if len(code) < 3:
            return render(request, "core/create_classroom.html",
                          {"error": "Join code must be at least 3 characters.", "name": name})
        if Classroom.objects.filter(join_code=code).exists():
            return render(request, "core/create_classroom.html",
                          {"error": f"The code '{code}' is already taken. Try another.", "name": name})
        Classroom.objects.create(teacher=request.user, name=name, join_code=code)
        return redirect("core:teacher_dashboard")
    return render(request, "core/create_classroom.html")


@login_required
def join_class(request):
    profile = _get_profile(request.user)
    # Teachers don't join classes
    if profile.is_teacher:
        return redirect("core:teacher_dashboard")

    error = None
    success = None

    if request.method == "POST":
        code = request.POST.get("class_code", "").strip().upper()
        if not code:
            error = "Please enter a classroom code."
        else:
            try:
                classroom = Classroom.objects.get(join_code=code)
                if profile.classroom == classroom:
                    error = f"You're already in '{classroom.name}'!"
                else:
                    profile.classroom = classroom
                    profile.save()
                    success = f"You've joined '{classroom.name}'! 🎉"
            except Classroom.DoesNotExist:
                error = f"Code '{code}' not found. Double-check with your teacher."

    return render(request, "core/join_class.html", {
        "profile": profile,
        "error":   error,
        "success": success,
    })
