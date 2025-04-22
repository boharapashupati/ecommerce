from django.shortcuts import render, redirect
from django.contrib import messages

def contact(request):
    """
    Contact page view that handles the contact form submission.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message', '')
        
        # Here you would typically send an email or save the contact message to the database
        # For now, we'll just add a success message
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
        
    return render(request, 'contact.html') 