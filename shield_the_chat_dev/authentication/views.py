from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from shield_the_chat import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token

#from django_otp.plugins.otp_totp import util

import qrcode
from django.core.files.base import ContentFile

import math
import random



# Create your views here.
def home(request):
    return render(request, "authentication/index.html")


def request1(request):
    if request.method == "POST":
        username1 = request.POST['username1']
        email1 = request.POST['email1']
        time = request.POST['chatTime']
        email2 = request.POST['email2']
        username2 = request.POST['username2']
        password2 = request.POST['password']
    

        # Attach QR code to the email
        send_mail(
            'Shield The Chat invite to chat',
            'Scan the QR code to authenticate.',
            'settings.EMAIL_HOST_USER',
            [email1],
            f"{username1}: You are invited to chat at {time}",
        )

        send_mail(
            'Shield The Chat invite to chat',
            'Scan the QR code to authenticate.',
            'settings.EMAIL_HOST_USER',
            [email2],
            f" {username2}: You requested to chat at {time}",
        )
        subject = 'Shield The Chat invite to chat'
        message =  f"{username1}: You are invited to chat at {time}"
        from_email = settings.EMAIL_HOST_USER
        to_email = [email1]

        email = EmailMessage(subject, message, from_email, to_email)
        email.send()

        subject = 'Shield The Chat invite to chat'
        message =   f" {username2}: You requested to chat at {time}"
        from_email = settings.EMAIL_HOST_USER
        to_email = [email2]

        email = EmailMessage(subject, message, from_email, to_email)
        email.send()

    
        messages.success(request, "Invited Sucessfully!!")
            
        return render(request, "authentication/index.html",{"fname":username2})

    return render(request, "send_invitation.html")

def qr_code_otp(user):

    digits="0123456789"
    OTP=""
    for i in range(6):
        OTP+=digits[math.floor(random.random()*10)]
        
    

    
    qrimage = qrcode.make(OTP)
    qrimage.save(f"{user.username}.jpg")

        

    # Send email with attachment
    subject = 'Your OTP QR Code'
    message = 'Please find your OTP QR Code attached.'
    from_email = settings.EMAIL_HOST_USER
    to_email = [user.email]

    email = EmailMessage(subject, message, from_email, to_email)
    email.attach_file(f"{user.username}.jpg")
    email.send()
    return OTP
    


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return render(request, "authentication/signup.html")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return render(request, "authentication/signup.html")
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return render(request, "authentication/signup.html")
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return render(request, "authentication/signup.html")
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return render(request, "authentication/signup.html")
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        
        # Welcome Email
        subject = "Welcome to Shield The Chat!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Shield The Chat!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nAnubhav Madhav"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Shield The Chat!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
        
        
    return render(request, "authentication/signup.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')

def otp_authentication(request):
    if request.method == 'POST':
        user = request.POST.get('user', '')
        entered_otp = request.POST.get('otp', '')
        # Replace this with your actual OTP verification logic
        expected_otp = str(otp)  # Change this to the expected OTP

        if entered_otp == expected_otp:
            messages.success(request, 'OTP Verified Successfully!')
            return  render(request, "authentication/index.html",{"fname":user}) 
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'authentication/otp.html')
otp = 0
def signin(request):
    global otp
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, "Logged In Sucessfully!!")
            otp = qr_code_otp(user)

            return render(request, "authentication/otp.html")
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "authentication/signin.html")

def chatPage(request, *args, **kwargs):
	context = {}
	return render(request, "chat/templates/chat/chatPage.html", context)

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')