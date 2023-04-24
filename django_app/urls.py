from django.urls import path
from . import views

urlpatterns = [
    path('', views.privacy_policy, name='privacy-policy'),
    path('rest/v1/calendar/init/', views.GoogleCalendarInitView.as_view()),
    path('rest/v1/calendar/redirect/',
         views.GoogleCalendarRedirectView.as_view(),
         name='redirect'),
]
