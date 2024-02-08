"""Feedback urls."""
from django.urls import path

from .views import FeedbackView

app_name = "feedback"

urlpatterns = [
    path("feedbacks/", FeedbackView.as_view(), name="feedback-view"),
]
