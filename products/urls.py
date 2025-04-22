from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductListView,
    CategoryListView,
    product_detail,
)

router = DefaultRouter()
router.register(r'products', ProductListView)
router.register(r'categories', CategoryListView)


urlpatterns = [
    path('', include(router.urls)),
    path('products-view/<int:pk>/', product_detail, name='product_detail'),
]