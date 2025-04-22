# cart/views.py
from django.shortcuts import render

#create your views here.
def cart_detail(request):

    return render(request, 'cart/cart_detail.html')  
