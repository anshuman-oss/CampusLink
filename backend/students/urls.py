from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("list", views.StudentViewSet, basename="students")

urlpatterns = [
    path("me/", views.MeView.as_view()),
    path("me/resume/", views.ResumeView.as_view()),
    path("me/skill-gap/", views.SkillGapView.as_view()),
    path("", include(router.urls)),
]