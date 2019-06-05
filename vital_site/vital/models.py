from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email,
                    password=None):
        user = self.model(email=email, password=password)
        user.set_password(user.password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,
                         password):
        user = self.create_user(email,
                                password=password)
        user.set_password(user.password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Intake_Period(models.Model):
    period_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.period_name


class VLAB_User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True, db_index=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    admitted_on = models.ForeignKey(Intake_Period, null=True, blank=True, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, null=True, on_delete=models.PROTECT)

    phone = models.CharField(max_length=200, null=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=50, null=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    sftp_account = models.CharField(max_length=200, unique=True)
    sftp_pass = models.CharField(max_length=200)
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.email

# class Blocked_User(models.Model):
#    user_id = models.IntegerField(default=0)
#    blocked_at = models.DateTimeField(default=datetime.now)


class User_Session(models.Model):
    user_id = models.IntegerField(default=0, unique=True)
    session_key = models.CharField(max_length=40)


class Allowed_Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    email_suffix = models.CharField(max_length=200)


class Course(models.Model):
    name = models.CharField(max_length=200)
    course_number = models.CharField(max_length=200, unique=True)
    registration_code = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(default=0)
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    status = models.CharField(max_length=10)
    auto_shutdown_after = models.IntegerField(default=3)
    allow_long_running_vms = models.BooleanField(default=False)
    no_of_students = models.IntegerField(default=0)

    def __str__(self):
        return self.course_number + ":" + self.name


class Virtual_Machine_Type(models.Model):
    name = models.CharField(max_length=200)
    icon_location = models.CharField(max_length=500)


class Virtual_Machine(models.Model):
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    type = models.ForeignKey(Virtual_Machine_Type, null=True)


class User_VM_Config(models.Model):
    xen_server = models.CharField(max_length=50)
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    vm = models.ForeignKey(Virtual_Machine,  on_delete=models.PROTECT)
    user_id = models.IntegerField(default=0)
    vnc_port = models.CharField(max_length=10)
    terminal_port = models.CharField(max_length=10)
    no_vnc_pid = models.CharField(max_length=10)
    token = models.CharField(max_length=50, null=True)


class Available_Config(models.Model):
    category = models.CharField(max_length=20)
    value = models.CharField(max_length=200)


class Network_Configuration(models.Model):
    name = models.CharField(max_length=10)
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    virtual_machine = models.ForeignKey(Virtual_Machine, on_delete=models.PROTECT)

    is_course_net = models.BooleanField(default=False)
    has_internet_access = models.BooleanField(default=False)


class User_Bridge(models.Model):
    name = models.CharField(max_length=15, primary_key=True)
    created = models.BooleanField(default=False)


class User_Network_Configuration(models.Model):
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    vm = models.ForeignKey(Virtual_Machine, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)

    user_id = models.IntegerField(default=0)
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    bridge = models.ForeignKey(User_Bridge, on_delete=models.PROTECT)
    mac_id = models.CharField(max_length=50)
    is_course_net = models.BooleanField(default=False)


class Faculty(models.Model):
    PROFESSOR = 'PR'
    TEACHING_ASSISTANT = 'TA'
    OWNER = 'OW'
    TYPE_CHOICES = (
        (PROFESSOR, 'Professor'),
        (TEACHING_ASSISTANT, 'TeachingAssistant'),
        (OWNER, 'Owner')
    )
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    user = models.ForeignKey(VLAB_User, null=True, on_delete=models.PROTECT)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=PROFESSOR)


class Registered_Course(models.Model):
    user_id = models.IntegerField(default=0)
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    registered_date = models.DateTimeField(default=datetime.now)


class Audit(models.Model):
    done_by = models.IntegerField()
    done_at = models.DateTimeField(default=datetime.now)
    action = models.CharField(max_length=500)


class Xen_Server(models.Model):
    name = models.CharField(max_length=50, unique=True)
    total_memory = models.IntegerField(default=0)
    used_memory = models.IntegerField(default=0)
    utilization = models.DecimalField(max_digits=5, decimal_places=4)
    no_of_vms = models.IntegerField(default=0)
    no_of_students = models.IntegerField(default=0)
    no_of_courses = models.IntegerField(default=0)
    status = models.CharField(max_length=10)


class Auto_Start_Resources(models.Model):
    name = models.CharField(max_length=15, unique=True)
    type = models.CharField(max_length=10)
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    course = models.ForeignKey(Course, on_delete=models.PROTECT)


#adding new tables for maintaing student local network MAC id's
class Local_Network_MAC_Address(models.Model):
    # added on_delete argument: https://www.valentinog.com/blog/django-missing-argument-on-delete/
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    network_configuration = models.ForeignKey(Network_Configuration, on_delete=models.PROTECT)

    mac_id = models.CharField(max_length=200)
