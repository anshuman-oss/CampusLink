from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("roster", views.RosterViewSet, basename="roster")

urlpatterns = [
    path("me/", views.MeView.as_view()),
    path("me/resume/", views.ResumeView.as_view()),
    path("me/skill-gap/", views.SkillGapView.as_view()),
    path("me/matches/", views.MyMatchesView.as_view()),
    path("", include(router.urls)),
]