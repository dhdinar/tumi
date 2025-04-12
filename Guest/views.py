from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from user.models import Room, House, Contact, User
import re

def index(request):
    template = loader.get_template('index.html')
    context = {}

    rooms = Room.objects.all()
    if rooms.exists():
        n = rooms.count()
        nslide = n // 3 + (n % 3 > 0)
        context['room'] = [rooms, range(1, nslide + 1), n]

    houses = House.objects.all()
    if houses.exists():
        n = houses.count()
        nslide = n // 3 + (n % 3 > 0)
        context['house'] = [houses, range(1, nslide + 1), n]

    return HttpResponse(template.render(context, request))


def home(request):
    return render(request, 'home.html', {'result': '', 'msg': 'Search your query'})


def search(request):
    template = loader.get_template('home.html')
    context = {}
    if request.method == 'GET':
        typ = request.GET.get('type')
        q = request.GET.get('q', '').lower()
        context.update({'type': typ, 'q': q})

        results = []
        if typ == 'House':
            results = House.objects.filter(location__iexact=q) | House.objects.filter(city__iexact=q)
        elif typ == 'Apartment':
            results = Room.objects.filter(location__iexact=q) | Room.objects.filter(city__iexact=q)

        if not results:
            messages.success(request, "No matching results for your query.")

        context['result'] = [results, results.count()]
    return HttpResponse(template.render(context, request))


def about(request):
    template = loader.get_template('about.html')
    context = {
        'room': Room.objects.all(),
        'house': House.objects.all(),
    }
    return HttpResponse(template.render(context, request))


def contact(request):
    template = loader.get_template('contact.html')
    context = {}
    if request.method == 'POST':
        subject = request.POST['subject']
        email = request.POST['email']
        body = request.POST['body']
        if not re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
            return render(request, 'contact.html', {'msg': 'Invalid email'})
        Contact.objects.create(subject=subject, email=email, body=body)
        context['msg'] = 'Message sent to admin.'
    else:
        context['msg'] = ''
    return HttpResponse(template.render(context, request))


def descr(request):
    template = loader.get_template('desc.html')
    context = {}
    if request.method == 'GET':
        prop_id = request.GET.get('id')
        try:
            room = Room.objects.get(room_id=prop_id)
            context.update({'val': room, 'type': 'Apartment', 'user': room.user})
        except Room.DoesNotExist:
            house = House.objects.get(house_id=prop_id)
            context.update({'val': house, 'type': 'House', 'user': house.user})
    return HttpResponse(template.render(context, request))


# def register(request):
#     if request.method == 'GET':
#         return render(request, 'register.html', {'msg': ''})

#     name = request.POST['name']
#     email = request.POST['email']
#     location = request.POST['location']
#     city = request.POST['city']
#     state = request.POST['state']
#     phone = request.POST['phone']
#     pas = request.POST['pass']
#     cpas = request.POST['cpass']

#     if not re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
#         return render(request, 'register.html', {'msg': 'Invalid email'})

#     if len(phone) != 10 or not phone.isdigit():
#         return render(request, 'register.html', {'msg': 'Invalid phone number'})

#     if pas != cpas:
#         return render(request, 'register.html', {'msg': 'Password did not match'})

#     if User.objects.filter(email=email).exists():
#         return render(request, 'register.html', {'msg': 'Email already registered'})

#     user = User.objects.create(
#         name=name,
#         email=email,
#         location=location,
#         city=city,
#         state=state,
#         number=phone,
#         password=pas
#     )
#     login(request, user)
#     return redirect("/profile/")


@login_required(login_url='/login')
def profile(request):
    report = Contact.objects.filter(email=request.user.email)
    room = Room.objects.filter(user_email=request.user.email)  # Updated field
    house = House.objects.filter(user_email=request.user.email)  # Updated field

    context = {
        'user': request.user,
        'report': report,
        'reportno': report.count(),
        'roomno': room.count(),
        'houseno': house.count(),
        'room': [room, range(1, (room.count() // 3) + 2), room.count()] if room.exists() else [],
        'house': [house, range(1, (house.count() // 3) + 2), house.count()] if house.exists() else []
    }
    return render(request, 'profile.html', context)


@login_required(login_url='/login')
def post(request):
    if request.method == "GET":
        return render(request, 'post.html', {'user': request.user})
    try:
        room = Room.objects.create(
            user_email=request.user.email,  # Updated field
            dimention=request.POST['dimention'],
            location=request.POST['location'].lower(),
            city=request.POST['city'].lower(),
            state=request.POST['state'].lower(),
            cost=int(request.POST['cost']),
            hall=request.POST['hall'].lower(),
            kitchen=request.POST['kitchen'].lower(),
            balcany=request.POST['balcany'].lower(),
            bedrooms=int(request.POST['bedroom']),
            AC=request.POST['AC'].lower(),
            desc=request.POST['desc'].upper(),
            img=request.FILES['img']
        )
        messages.success(request, 'Apartment posted successfully.')
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    return render(request, 'post.html')


@login_required(login_url='/login')
def posth(request):
    if request.method == "GET":
        return render(request, 'posth.html', {'user': request.user})
    try:
        house = House.objects.create(
            user_email=request.user.email,  # Updated field
            area=request.POST['area'],
            floor=request.POST['floor'],
            location=request.POST['location'].lower(),
            city=request.POST['city'].lower(),
            state=request.POST['state'].lower(),
            cost=int(request.POST['cost']),
            hall=request.POST['hall'].lower(),
            kitchen=request.POST['kitchen'].lower(),
            balcany=request.POST['balcany'].lower(),
            bedrooms=int(request.POST['bedroom']),
            AC=request.POST['AC'].lower(),
            desc=request.POST['desc'].upper(),
            img=request.FILES['img']
        )
        messages.success(request, 'House posted successfully.')
    except Exception as e:
        print(e)
        return HttpResponse(status=500)
    return render(request, 'posth.html')


@login_required(login_url='/login')
def deleter(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        Room.objects.filter(room_id=id, user_email=request.user.email).delete()  # Updated field
        messages.success(request, 'Apartment deleted successfully.')
    return redirect('/profile')


@login_required(login_url='/login')
def deleteh(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        House.objects.filter(house_id=id, user_email=request.user.email).delete()  # Updated field
        messages.success(request, 'House deleted successfully.')
    return redirect('/profile')


# def login_view(request):
#     if request.method == 'GET':
#         return render(request, 'login.html')
#     email = request.POST['email']
#     password = request.POST['password']
#     user = authenticate(request, email=email, password=password)
#     if user:
#         login(request, user)
#         return redirect("/")
#     else:
#         return render(request, 'login.html', {'msg': 'Email and password did not match.'})


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {'msg': ''})

    name = request.POST['name']
    email = request.POST['email']
    #location = request.POST['location']
    #city = request.POST['city']
    #state = request.POST['state']
    #phone = request.POST['phone']
    pas = request.POST['pass']
    #cpas = request.POST['cpass']

    if not re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
        return render(request, 'register.html', {'msg': 'Invalid email'})

    #if len(phone) != 10 or not phone.isdigit():
    #    return render(request, 'register.html', {'msg': 'Invalid phone number'})

    #if pas != cpas:
    #    return render(request, 'register.html', {'msg': 'Password did not match'})

    if User.objects.filter(email=email).exists():
        return render(request, 'register.html', {'msg': 'Email already registered'})

    # Create user with hashed password
    user = User.objects.create(
        name=name,
        email=email,
        #location=location,
        #city=city,
        #state=state,
        #number=phone,
        password=make_password(pas)  # Hash the password using Django's make_password
    )
    
    # You'll also need to update your login function to use Django's authentication system
    user = authenticate(request, email=email, password=pas)
    if user:
        login(request, user)
        return redirect("/profile/")
    else:
        # This shouldn't happen if user creation was successful, but just in case
        return render(request, 'register.html', {'msg': 'Registration failed. Please try again.'})


def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, email=email, password=password)
    if user:
        login(request, user)
        return redirect("/")
    else:
        return render(request, 'login.html', {'msg': 'Email and password did not match.'})