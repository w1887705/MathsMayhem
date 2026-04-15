from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("",                                  views.tasks,              name="tasks"),
    path("tasks/",                            views.tasks,              name="tasks"),
    path("tasks/<slug:slug>/",                views.task_detail,        name="task_detail"),
    path("tasks/<slug:slug>/save/",           views.save_progress,      name="save_progress"),
    path("shop/",                             views.shop,               name="shop"),
    path("shop/buy/<int:item_id>/",           views.buy_item,           name="buy_item"),
    path("register/",                         views.register,           name="register"),
    path("join-class/",                       views.join_class,         name="join_class"),
    path("teacher/",                          views.teacher_dashboard,  name="teacher_dashboard"),
    path("teacher/create-class/",             views.create_classroom,   name="create_classroom"),
    path("teacher/student/<int:user_id>/",    views.student_detail,     name="student_detail"),
]
# already imported views above
