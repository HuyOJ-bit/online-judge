from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chat.urls")),
    path("", include("judge.urls")),
]

admin.site.site_header = "Hùng Vương Online Judge - Quản trị"
admin.site.site_title = "Hùng Vương Online Judge - Quản trị"
admin.site.index_title = "Quản trị hệ thống"
