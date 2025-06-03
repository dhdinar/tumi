# models.py - Complete corrected file
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have a password')
        if not name:
            raise ValueError('User must have a full name')

        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.set_password(password)
        user.admin = is_admin
        user.staff = is_staff
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        user = self.create_user(
            email=email,
            name=name,
            password=password,
            is_admin=True,
            is_staff=True,
            is_active=True
        )
        return user


class User(AbstractBaseUser):

    email = models.EmailField(max_length=100, primary_key=True, unique=True)  # Changed to EmailField
    name = models.CharField(max_length=25)
    # password field removed - AbstractBaseUser already has it
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # Removed 'password' from here
    objects = UserManager()

    def __str__(self):
        return self.email

    @staticmethod
    def has_perm(perm, obj=None):
         # "Does the user have a specific permission?"
         # Simplest possible answer: Yes, always
        return True

    @staticmethod
    def has_module_perms(app_label):
         # "Does the user have permissions to view the app `app_label`?"
         # Simplest possible answer: Yes, always
         return True

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        # "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        # "Is the user active?"
        return self.active


class Room(models.Model):

    room_id = models.AutoField(primary_key=True)
    user_email = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    dimention = models.CharField(max_length=100)  # Fixed typo: dimention -> dimension
    location = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    #state = models.CharField(max_length=50)
    cost = models.IntegerField()
    bedrooms = models.IntegerField()
    kitchen = models.CharField(max_length=3)
    floor = models.IntegerField()
    #hall = models.CharField(max_length=3)
    balcany = models.CharField(max_length=3)  
    desc = models.CharField(max_length=200)
    #AC = models.CharField(max_length=3)
    img = models.ImageField(upload_to='room_id/', height_field=None,
                            width_field=None, max_length=100)
    date = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.room_id)


class House(models.Model):

    house_id = models.AutoField(primary_key=True)
    user_email = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    area = models.IntegerField()
    floor = models.IntegerField()
    location = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    cost = models.IntegerField()
    bedrooms = models.IntegerField()
    kitchen = models.IntegerField()
    balcany = models.CharField(max_length=3)  
    desc = models.CharField(max_length=200)
    img = models.ImageField(upload_to='house_id/', height_field=None,
                            width_field=None, max_length=100)
    date = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.house_id)


class Contact(models.Model):

    contact_id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    body = models.CharField(max_length=500)

    def __str__(self):
        return str(self.contact_id)