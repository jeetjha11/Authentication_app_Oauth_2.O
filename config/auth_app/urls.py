
from django.urls import path

from .views import home_views,logout_view,dashboard_view
urlpatterns = [
    path('', home_views),
    path('logout', logout_view),
    path('dashboard', dashboard_view),


]