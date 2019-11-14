from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from vital.models import Virtual_Machine, VLAB_User, Course, Registered_Course, User_VM_Config
from vital.utils import XenClient
from django.db import transaction

class Command(BaseCommand):
    help = "To Test Parallel VM Creation"

    def add_arguments(self, parser):
        parser.add_argument(
            '-s', '--Student ID',
            action='store',
            dest='student_id',
            help='specify student id',
            required=True
        )
        parser.add_argument(
            '-c', '--course_id',
            action='store',
            dest='course_id',
            help='specify course id of user',
            required=True
        )
        parser.add_argument(
            '-a', '--action',
            action='store',
            dest='action',
            help='specify action for the V<s',
            required=True
        )

    def handle(self, *args, **options):
        student_id = options['student_id']
        course_id = options['course_id']
        action = options['action']
        user = VLAB_User.objects.get(id = student_id)
        r = Registered_Course.objects.filter(course_id=course_id, user_id=user.id)
        print(r.count())
        if (len(Registered_Course.objects.filter(course_id=course_id, user_id=user.id))) < 1:
            print("User Not Registered for Course")
            return
        course = Course.objects.get(id=course_id)
        for vm in course.virtual_machine_set.all():
            print(vm.id)
            if action == 'start':
                self.start_vm(user, course_id, vm.id)
            elif action == 'stop':
                self.stop_vm(user, course_id, vm.id)

    def start_vm(self, user, course_id, vm_id):
        print('Starting vm - {}_{}_{}'.format(user.id, course_id, vm_id))
        config = User_VM_Config()
        started_vm = None
        vm = None
        try:
            vm = Virtual_Machine.objects.get(pk=vm_id)
            with transaction.atomic():
                config.vm = vm
                config.user_id = user.id
                # start vm with xen api which returns handle to the vm
                started_vm = XenClient().start_vm(user, course_id, vm_id)
                config.vnc_port = started_vm['vnc_port']
                config.xen_server = started_vm['xen_server']

                config.save()
        except Virtual_Machine.DoesNotExist as e:
            print(str(e))
        except Exception as e:
            print(str(e))
            if 'Connection refused' not in str(e).rstrip() or started_vm is not None:
                XenClient().remove_network_bridges(vm.xen_server, user, course_id, vm_id)
                XenClient().stop_vm(started_vm['xen_server'], user, course_id, vm_id)

    def stop_vm(self, user, course_id, vm_id):
        print('Stopping vm - {}_{}_{}'.format(user.id, course_id, vm_id))
        virtual_machine = Virtual_Machine.objects.get(pk=vm_id)
        vm = User_VM_Config.objects.get(user_id=user.id, vm_id=vm_id)

        try:
            XenClient().remove_network_bridges(vm.xen_server, user, course_id, vm_id)
            XenClient().stop_vm(vm.xen_server, user, course_id, vm_id)

            print('Stopped vm - {}_{}_{}'.format(user.id, course_id, vm_id))
        except Exception as e:
            raise e
