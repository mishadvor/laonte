from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("catalog/", views.catalog, name="catalog"),  # <-- Новая страница
    path(
        "category/<slug:category_slug>/",
        views.product_list,
        name="product_list_by_category",
    ),
    path(
        "category/<slug:category_slug>/products/",
        views.category_products,
        name="category_products",
    ),
    path("", views.product_list, name="product_list"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("size-chart/", views.size_chart, name="size_chart"),
    path("contact/", views.contact, name="contact"),
    path("add-to-order/", views.add_to_order, name="add_to_order"),
    path("order/", views.view_order, name="view_order"),
    path("order/submit/", views.submit_order, name="submit_order"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
