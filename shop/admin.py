from django.contrib import admin
from .models import Product, Category, Size, ProductSize, Order, OrderItem, ProductImage


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


# --- Регистрация Product (все inlines вместе) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "available", "is_new", "is_sale")
    list_filter = ("available", "category", "is_new", "is_sale")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductSizeInline, ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # readonly_fields = ("product_size", "quantity")  ← Закомментируй или удали
    fields = ("product_size", "quantity")  # ← Используй fields
    can_delete = False
    show_change_link = True  # ← Это включит ссылку "Изменить"


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


admin.register(OrderItem)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "size", "quantity")
    list_filter = ("order", "product__product__name")
    readonly_fields = ("order", "product", "size", "quantity")

    def product(self, obj):
        return obj.product_size.product.name

    product.short_description = "Товар"

    def size(self, obj):
        return obj.product_size.size.name

    size.short_description = "Размер"
