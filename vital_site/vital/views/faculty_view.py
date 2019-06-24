from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Faculty, Course, Virtual_Machine, Registered_Course
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
def advising_courses(request):
    logger.debug("In registered courses")
    faculty_records = Faculty.objects.filter(user_id=request.user.id)
    adv_courses = []
    for faculty in faculty_records:
        logger.debug(faculty)
        adv_courses.append(faculty.course)
    return render(request, 'vital/advising_courses.html', {'advising_courses': adv_courses})


@login_required(login_url='/login/')
def course_detail(request, course_id):
    logger.debug("in course detail")
    professors = ''
    teaching_assistants = ''
    is_prof = False
    faculty_self = Faculty.objects.filter(course_id=course_id, user_id=request.user.id)
    if len(faculty_self) == 1 and faculty_self[0].type == 'PR':
        is_prof = True

    try:
        course = Course.objects.get(pk=course_id)
        faculties = course.faculty_set.all()
        for faculty in faculties:
            if faculty.type == 'OW' or faculty.type == 'PR':
                professors = professors + ',' + ("%s %s" % (faculty.user.first_name, faculty.user.last_name))
            else:
                teaching_assistants = teaching_assistants + ', ' + ("%s %s" % (faculty.user.first_name, faculty.user.last_name))
        virtual_machines = Virtual_Machine.objects.filter(course_id=course_id)
        students_registered = len(Registered_Course.objects.filter(course_id=course_id))
    except Course.DoesNotExist:
        logger.error("Course being searched for cannot be found - course id:%d, user id:%d" % (course_id,
                                                                                               request.user.id))
    return render(request, 'vital/course_detail.html', {'virtual_machines': virtual_machines, 'course': course,
                                                        'professors': professors[1:],
                                                        'students_registered': students_registered,
                                                        'teaching_assistants': teaching_assistants[1:],
                                                        'is_prof':is_prof})
