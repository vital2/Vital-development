from django.conf.urls import url

from . import views

app_name = 'authoring'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^courses/home/$', views.course_home, name='course_home'),
    url(r'^courses/create/$', views.course_create, name='course_create'),
    url(r'^courses/addvms', views.course_add_vms, name='course_add_vms'),
    url(r'^courses/networking', views.course_networking, name='course_networking'),
    url(r'^courses/summary', views.course_summary, name='course_summary'),
    url(r'^courses/vms/$', views.course_vm_setup, name='course_vms'),
    url(r'^courses/destroy/$', views.course_destroy, name='course_destroy'),
]

