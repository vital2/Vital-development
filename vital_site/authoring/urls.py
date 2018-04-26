from django.conf.urls import url

from . import views

app_name = 'authoring'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^courses/home/$', views.course_home, name='course_home'),
    url(r'^courses/create/$', views.course_create, name='course_create'),
    url(r'^courses/id/(?P<course_id>[0-9]+)/vms', views.course_add_vms, name='author_course_add_vms'),
    url(r'^courses/vms/$', views.course_vm_setup, name='course_vms'),
    url(r'^courses/destroy/$', views.course_destroy, name='course_destroy'),
]
