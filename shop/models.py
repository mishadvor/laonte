from django.db import models


class Category(models.Model):
    name = models.CharField("Категория", max_length=100)
    slug = models.SlugField("URL", unique=True)
    icon = models.CharField(
        "Иконка Font Awesome",
        max_length=50,
        blank=True,
        help_text="Например: fa-dress, fa-pants",
    )
    image = models.ImageField(
        "Фото категории",
        upload_to="categories/",
        blank=True,
        help_text="Опционально: фото вместо иконки",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
    )
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("URL", unique=True, blank=True)
    article = models.CharField("Артикул", max_length=50, blank=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена опт", max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        "Старая цена", max_digits=10, decimal_places=2, blank=True, null=True
    )
    image = models.ImageField("Изображение", upload_to="products/", blank=True)
    available = models.BooleanField("В наличии", default=True)
    is_new = models.BooleanField("Новинка", default=False)
    is_sale = models.BooleanField("Распродажа", default=False)
    created = models.DateTimeField(auto_now_add=True)
    image_main = models.ImageField("Основное фото", upload_to="products/", blank=True)
    image_back = models.ImageField("Фото сзади", upload_to="products/", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Size(models.Model):
    name = models.CharField("Размер", max_length=10)  # например: 48, 50, XL, 2XL
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
        ordering = ["sort_order"]


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    stock = models.PositiveIntegerField("В наличии (шт)", default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size.name}"

    class Meta:
        verbose_name = "Размер товара"
        verbose_name_plural = "Размеры товаров"


class Order(models.Model):
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField("Обработано", default=False)

    def __str__(self):
        return f"Заявка {self.id} от {self.name}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заявка")
    product_size = models.ForeignKey(
        ProductSize, on_delete=models.CASCADE, verbose_name="Размер товара"
    )
    quantity = models.PositiveIntegerField("Количество")

    def __str__(self):
        return f"{self.quantity} x {self.product_size}"

    class Meta:
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявок"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    image = models.ImageField("Фото", upload_to="products/")
    is_main = models.BooleanField("Основное фото", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)

    def __str__(self):
        return f"Фото {self.product.name}"

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
        ordering = ["order"]
