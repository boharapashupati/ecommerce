from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse

class ProductListView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']

    def get_queryset(self):
        queryset = Product.objects.all()
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        return queryset

class CategoryListView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

def home(request):
    # Get featured products (products marked as featured)
    featured_products = Product.objects.filter(is_featured=True)[:8]
    
    # Get all categories
    categories = Category.objects.all()[:6]
    
    # Get special offers (you can create a separate model for this later)
    special_offers = [
        {
            'title': 'Summer Sale',
            'description': 'Get up to 50% off on selected items',
            'link': '/products/?sale=true'
        },
        {
            'title': 'New Arrivals',
            'description': 'Check out our latest products',
            'link': '/products/?new=true'
        }
    ]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'special_offers': special_offers,
    }
    
    return render(request, 'home.html', context)

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Here you would typically save the email to a database
        # For now, we'll just show a success message
        messages.success(request, 'Thank you for subscribing to our newsletter!')
        return redirect('home')
    return redirect('home')




def product_detail(request):
    return render(request, 'products/product_detail.html')
