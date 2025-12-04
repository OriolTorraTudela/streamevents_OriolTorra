from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list_view, name="event_list"),
    path("create/", views.event_create_view, name="event_create"),
    path("my-events/", views.my_events_view, name="my_events"),
    path("category/<str:category>/", views.events_by_category_view, name="events_by_category"),
    path("<int:pk>/", views.event_detail_view, name="event_detail"),
    path("<int:pk>/edit/", views.event_update_view, name="event_update"),
    path("<int:pk>/delete/", views.event_delete_view, name="event_delete"),
    path("api/tags-autocomplete/", views.tags_autocomplete_view, name="tags_autocomplete"),
]
