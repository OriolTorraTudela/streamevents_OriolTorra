from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # HOME
    path('', home_view, name="home"),

    # USERS
    path("users/", include("users.urls", namespace="users")),

    # EVENTS 
    path("events/", include(("events.urls", "events"), namespace="events")),
    
    # CHAT
    path("chat/", include("chat.urls", namespace="chat")),

    # Cerca-Semantica
    path("", include("semantic_search.urls")),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
