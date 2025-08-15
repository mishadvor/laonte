from django.shortcuts import render
from django.db.models import Q
from .models import Product, Category
from django.core.mail import send_mail
from .forms import ContactForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category, Size, ProductSize, Order, OrderItem


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()

    # Начинаем с базового набора товаров
    products = Product.objects.filter(available=True)

    # Поиск по названию или артикулу
    query = request.GET.get("q")
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(article__icontains=query)
        )

    # Фильтрация по категории
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Добавляем скидку к каждому товару
    for product in products:
        if product.old_price and product.old_price > 0:
            discount = (product.old_price - product.price) / product.old_price * 100
            product.discount_percent = int(discount)
        else:
            product.discount_percent = 0

    # Товары недели (например, с пометкой "Распродажа")
    weekly_products = Product.objects.filter(is_sale=True, available=True)[:6]

    # Добавляем скидку и для weekly_products
    for product in weekly_products:
        if product.old_price and product.old_price > 0:
            discount = (product.old_price - product.price) / product.old_price * 100
            product.discount_percent = int(discount)
        else:
            product.discount_percent = 0

    return render(
        request,
        "shop/product/list.html",
        {
            "category": category,
            "categories": categories,
            "products": products,
            "weekly_products": weekly_products,
            "query": query,
        },
    )


def size_chart(request):
    return render(request, "shop/size_chart.html")


def product_detail(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    sizes = product.productsize_set.filter(stock__gt=0)

    # Получаем все фото товара
    images = product.images.all()

    # Определяем главное фото: сначала is_main=True, иначе — первое в списке
    main_image = images.filter(is_main=True).first()
    if not main_image and images.exists():
        main_image = images.first()

    # Товары недели для рекомендаций
    weekly_products = Product.objects.filter(is_sale=True, available=True)[:6]

    return render(
        request,
        "shop/product/detail.html",
        {
            "product": product,
            "sizes": sizes,
            "images": images,
            "main_image": main_image,  # ← Передаём в шаблон
            "weekly_products": weekly_products,
        },
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                subject=f"Новый запрос от {cd['name']}",
                message=f"Имя: {cd['name']}\nТелефон: {cd['phone']}\nСообщение: {cd['message']}",
                from_email="site@laonte.ru",
                recipient_list=["manager@laonte.ru"],
                fail_silently=False,
            )
            return render(request, "shop/contact_success.html")
    else:
        form = ContactForm()
    return render(request, "shop/contact.html", {"form": form})


def add_to_order(request):
    if request.method == "POST":
        product_size_id = request.POST.get("size")
        quantity = request.POST.get("quantity")

        order = request.session.get("order", [])
        item = {"product_size_id": product_size_id, "quantity": quantity}
        order.append(item)
        request.session["order"] = order
        messages.success(request, "Товар добавлен в заявку!")

    return redirect(request.META.get("HTTP_REFERER", "product_list"))


def view_order(request):
    """
    Отображает текущую заявку из сессии
    """
    order = request.session.get("order", [])
    items = []
    total_quantity = 0

    for item in order:
        try:
            product_size = ProductSize.objects.get(id=item["product_size_id"])
            items.append(
                {
                    "product_size": product_size,
                    "quantity": int(item["quantity"]),
                    "total_price": product_size.product.price * int(item["quantity"]),
                }
            )
            total_quantity += int(item["quantity"])
        except ProductSize.DoesNotExist:
            continue  # Пропускаем удалённые товары

    return render(
        request,
        "shop/order/view.html",
        {"items": items, "total_quantity": total_quantity},
    )


def submit_order(request):
    """
    Обрабатывает отправку заявки
    """
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        # Создаём новую заявку в базе данных
        order = Order.objects.create(name=name, phone=phone, email=email)

        # Добавляем позиции из сессии
        session_order = request.session.get("order", [])
        for item in session_order:
            try:
                product_size = ProductSize.objects.get(id=item["product_size_id"])
                OrderItem.objects.create(
                    order=order, product_size=product_size, quantity=item["quantity"]
                )
            except ProductSize.DoesNotExist:
                continue  # Пропускаем, если размер был удалён

        # Отправляем email менеджеру
        send_mail(
            subject=f"Новая заявка №{order.id} от {name}",
            message=f"""
                Имя: {name}
                Телефон: {phone}
                Email: {email}

                Заявка содержит {len(session_order)} позиций.
                Детали: http://127.0.0.1:8000/admin/shop/order/{order.id}/
            """,
            from_email="site@laonte.ru",
            recipient_list=["manager@laonte.ru"],
            fail_silently=False,
        )

        # Очищаем сессию после отправки
        del request.session["order"]

        # Показываем сообщение об успехе
        messages.success(
            request,
            "Ваша заявка успешно отправлена! Менеджер свяжется с вами в ближайшее время.",
        )
        return redirect("product_list")

    # Если GET-запрос — показываем форму
    return render(request, "shop/order/submit.html")


def catalog(request):
    """
    Страница "Каталог" — показывает все категории и количество активных товаров
    """
    categories = Category.objects.all().order_by("name")

    # Добавляем количество доступных товаров
    for category in categories:
        category.product_count = category.product_set.filter(available=True).count()

    return render(request, "shop/catalog.html", {"categories": categories})


# views.py
def catalog(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    query = request.GET.get("q")
    category_slug = request.GET.get("category")

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(article__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(
        request,
        "shop/catalog.html",
        {"products": products, "categories": categories, "query": query},
    )


def category_products(request, category_slug):
    """
    Только товары из выбранной категории
    """
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(available=True, category=category)

    # Добавляем скидки
    for product in products:
        if product.old_price and product.old_price > 0:
            discount = (product.old_price - product.price) / product.old_price * 100
            product.discount_percent = int(discount)
        else:
            product.discount_percent = 0

    return render(
        request,
        "shop/product/category_list.html",
        {"category": category, "products": products},
    )
