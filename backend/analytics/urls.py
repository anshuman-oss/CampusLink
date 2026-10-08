from django.urls import path
from . import views
urlpatterns = [
    path("summary/", views.SummaryView.as_view()),
    path("at-risk/", views.AtRiskView.as_view()),
]