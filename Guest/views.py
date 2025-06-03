from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LogoutView
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
    return render(request, 'about.html', {
        'room': Room.objects.all(),
        'house': House.objects.all(),
    })


def contact(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        email = request.POST['email']
        body = request.POST['body']
        if not re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
            return render(request, 'contact.html', {'msg': 'Invalid email'})
        Contact.objects.create(subject=subject, email=email, body=body)
        return render(request, 'contact.html', {'msg': 'Message sent to admin.'})
    return render(request, 'contact.html', {'msg': ''})


def descr(request):
    if request.method == 'GET':
        prop_id = request.GET.get('id')

        if not prop_id:
            raise Http404("Property ID is required")

        try:
            prop_id = int(prop_id)
        except (ValueError, TypeError):
            raise Http404("Invalid property ID")

        try:
            room = get_object_or_404(Room, room_id=prop_id)
            context = {'val': room, 'type': 'Apartment', 'user': room.user_email}
        except Http404:
            house = get_object_or_404(House, house_id=prop_id)
            context = {'val': house, 'type': 'House', 'user': house.user_email}

        return render(request, 'desc.html', context)


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {'msg': ''})

    name = request.POST['name']
    email = request.POST['email']
    pas = request.POST['pass']

    if not re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
        return render(request, 'register.html', {'msg': 'Invalid email'})

    if User.objects.filter(email=email).exists():
        return render(request, 'register.html', {'msg': 'Email already registered'})

    user = User.objects.create(
        name=name,
        email=email,
        password=make_password(pas)  # hash password
    )

    # Authenticate and log in
    user = authenticate(request, email=email, password=pas)
    if user:
        login(request, user)
        return redirect("/profile/")
    return render(request, 'register.html', {'msg': 'Registration failed. Try again.'})


def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    email = request.POST['email']
    password = request.POST['password']

    user = authenticate(request, email=email, password=password)
    if user:
        login(request, user)
        return redirect("/")
    return render(request, 'login.html', {'msg': 'Email and password did not match.'})


@login_required(login_url='/login')
def profile(request):
    report = Contact.objects.filter(email=request.user.email)
    room = Room.objects.filter(user_email=request.user.email)
    house = House.objects.filter(user_email=request.user.email)

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
        Room.objects.create(
            user_email=request.user,
            dimention=request.POST['dimention'],
            location=request.POST['location'].lower(),
            city=request.POST['city'].lower(),
            floor=request.POST['floor'],
            cost=int(request.POST['cost']),
            kitchen=request.POST['kitchen'].lower(),
            balcany=request.POST['balcany'].lower(),
            bedrooms=int(request.POST['bedroom']),
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
        House.objects.create(
            user_email=request.user,
            area=request.POST['area'],
            floor=request.POST['floor'],
            location=request.POST['location'].lower(),
            city=request.POST['city'].lower(),
            cost=int(request.POST['cost']),
            kitchen=request.POST['kitchen'].lower(),
            balcany=request.POST['balcany'].lower(),
            bedrooms=int(request.POST['bedroom']),
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
        Room.objects.filter(room_id=id, user_email=request.user.email).delete()
        messages.success(request, 'Apartment deleted successfully.')
    return redirect('/profile')


@login_required(login_url='/login')
def deleteh(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        House.objects.filter(house_id=id, user_email=request.user.email).delete()
        messages.success(request, 'House deleted successfully.')
    return redirect('/profile')
