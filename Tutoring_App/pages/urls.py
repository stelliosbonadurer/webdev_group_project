# pages/urls.py
from django.urls import path
from .views import HomePageView, TAProfileEditView, TAProfileDetailView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("ta/edit/", TAProfileEditView.as_view(), name="ta_edit"),
    path("ta/<int:pk>/", TAProfileDetailView.as_view(), name="ta_view"),
]