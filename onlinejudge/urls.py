from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chat.urls")),
    path("", include("judge.urls")),
]

admin.site.site_header = "Online Judge — Administration"
admin.site.site_title = "Online Judge Admin"
admin.site.index_title = "Judge management"
