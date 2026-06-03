from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from .forms import OrderForm, OrderItemFormSet, ProductForm
from .models import Order, Product, Role, Supplier


def user_role(user):
    if not user.is_authenticated:
        return ""
    return user.role.name if user.role else ""


class UserLoginView(LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        return user_role(self.request.user) in self.allowed_roles


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.ADMIN,)


class ManagerOrAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (Role.MANAGER, Role.ADMIN)


class ProductListView(ListView):
    model = Product
    template_name = "core/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = Product.objects.select_related("supplier", "manufacturer", "category")
        if user_role(self.request.user) not in (Role.MANAGER, Role.ADMIN):
            return queryset

        search = self.request.GET.get("search", "").strip()
        if search:
            # Поиск должен работать сразу по всем текстовым данным товара и связанным справочникам.
            queryset = queryset.filter(
                Q(article__icontains=search)
                | Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(supplier__name__icontains=search)
                | Q(manufacturer__name__icontains=search)
                | Q(category__name__icontains=search)
            )

        supplier = self.request.GET.get("supplier")
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)

        sort_map = {
            "quantity_asc": "quantity",
            "quantity_desc": "-quantity",
        }
        sort = self.request.GET.get("sort")
        if sort in sort_map:
            queryset = queryset.order_by(sort_map[sort])
        return queryset

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["can_use_filters"] = user_role(self.request.user) in (Role.MANAGER, Role.ADMIN)
        context["can_edit_products"] = user_role(self.request.user) == Role.ADMIN
        context["suppliers"] = Supplier.objects.all()
        context["current"] = self.request.GET
        return context


class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        messages.success(self.request, "Товар добавлен.")
        return super().form_valid(form)


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        messages.success(self.request, "Товар обновлен.")
        return super().form_valid(form)


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Нельзя удалить товар, который есть в заказе.")
            return redirect(self.success_url)
        messages.success(self.request, "Товар удален.")
        return response


class OrderListView(ManagerOrAdminRequiredMixin, LoginRequiredMixin, ListView):
    model = Order
    template_name = "core/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.select_related("pickup_point", "client").prefetch_related(
            "items__product"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_edit_orders"] = user_role(self.request.user) == Role.ADMIN
        return context


class OrderFormsetMixin(AdminRequiredMixin):
    model = Order
    form_class = OrderForm
    template_name = "core/order_form.html"
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = OrderItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if not formset.is_valid():
            return self.form_invalid(form)
        # Сначала сохраняем заказ, затем привязываем к нему строки состава заказа.
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        messages.success(self.request, "Заказ сохранен.")
        return redirect(self.success_url)


class OrderCreateView(OrderFormsetMixin, CreateView):
    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)


class OrderUpdateView(OrderFormsetMixin, UpdateView):
    pass


class OrderDeleteView(AdminRequiredMixin, DeleteView):
    model = Order
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("order_list")

    def form_valid(self, form):
        messages.success(self.request, "Заказ удален.")
        return super().form_valid(form)
