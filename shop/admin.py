from django.contrib import admin
from .models import (
    Product,
    Category,
    Size,
    ProductSize,
    Order,
    OrderItem,
    ProductImage,
    SiteSettings,
    AboutUs,
)


# --- Регистрация модели Size ---
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    ordering = ("sort_order",)


# --- Inline: размеры товара (ProductSize) ---
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


# --- Inline: дополнительные фото товара ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "is_main", "order")


# --- Регистрация Product (обновлено!) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price_display",  # ← изменено
        "available",
        "is_new",
        "is_sale",
    )
    list_filter = (
        "available",
        "category",
        "is_new",
        "is_sale",
        "price_type",
    )  # ← добавлен price_type
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductSizeInline, ProductImageInline]

    # ===== НОВЫЕ ПОЛЯ В ФОРМЕ =====
    fieldsets = (
        (
            "Основное",
            {"fields": ("category", "name", "slug", "article", "description")},
        ),
        (
            "Цена",
            {
                "fields": ("price_type", "price", "price_custom_text", "old_price"),
                "description": "Выберите тип цены: 'Числовая цена' для обычной цены, 'Текстовая цена' для текста (например 'По запросу')",
            },
        ),
        ("Изображения", {"fields": ("image", "image_main", "image_back")}),
        ("Статус", {"fields": ("available", "is_new", "is_sale")}),
    )

    def price_display(self, obj):
        """Отображение цены в списке товаров"""
        if obj.price_type == "custom" and obj.price_custom_text:
            return f"📞 {obj.price_custom_text}"
        elif obj.price is None or obj.price == 0:
            return "💰 По запросу"
        else:
            return f"{obj.price} ₽"

    price_display.short_description = "Цена"

    # ===== ПОДСКАЗКИ ДЛЯ ПОЛЕЙ =====
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Делаем price необязательным, если выбран 'custom'
        if obj and obj.price_type == "custom":
            form.base_fields["price"].required = False
        return form


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product_size", "quantity")
    can_delete = False
    show_change_link = True


# --- Регистрация Order (заявка) ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "created", "processed")
    list_filter = ("processed", "created")
    readonly_fields = ("created",)
    inlines = [OrderItemInline]
    fieldsets = (
        ("Клиент", {"fields": ("name", "phone", "email")}),
        ("Статус", {"fields": ("processed", "created")}),
    )
    search_fields = ("name", "phone", "email")


# --- Регистрация Category ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "size", "quantity")
    list_filter = ("order",)
    readonly_fields = ("order", "product_size", "quantity")

    def product(self, obj):
        return obj.product_size.product.name

    product.short_description = "Товар"

    def size(self, obj):
        return obj.product_size.size.name

    size.short_description = "Размер"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("company_name", "phone", "email")
    fieldsets = (
        ("Компания", {"fields": ("company_name",)}),
        ("Контакты", {"fields": ("phone", "phone_extra", "email", "address")}),
        ("График", {"fields": ("work_hours",)}),
        (
            "Соцсети",
            {
                "fields": ("vk_link", "telegram_link", "instagram_link"),
                "classes": ("collapse",),
            },
        ),
        ("Подвал", {"fields": ("footer_text",)}),
    )


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    list_editable = ("is_active",)
