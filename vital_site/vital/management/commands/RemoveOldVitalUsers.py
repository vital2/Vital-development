from django.core.management.base import BaseCommand, CommandError
import logging
from django.utils import timezone
from vital.models import VLAB_User, Registered_Course, User_Network_Configuration, Available_Config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "removes all  STUDENTS who registered for vital account 2 years ago. " \
           "Users marked faculty/admin/staff will not be removed."

    def handle(self, *args, **options):
        two_years = timezone.now() + timezone.timedelta(days=-730)
        users = VLAB_User.objects.filter(created_date__lte=two_years)
        # is there a better way to check if there are VMs running for these users
        for user in users:
            Registered_Course.objects.filter(user_id=user.id).delete()
            user_nets = User_Network_Configuration.objects.filter(user_id=user.id)
            for net in user_nets:
                conf = Available_Config()
                conf.category = 'MAC_ADDR'
                conf.value = net.mac_id
                conf.save()
                net.delete()
            VLAB_User.objects.get(id=user.id).delete()
