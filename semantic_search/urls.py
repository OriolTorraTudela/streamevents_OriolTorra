from django.urls import path
from .views import semantic_search

app_name = "semantic_search"

urlpatterns = [
    path("semantic/", semantic_search, name="semantic"),
]
