from django.core.management.base import BaseCommand, CommandError
from vital.models import Available_Config


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('message', type=str)

    def handle(self, *args, **options):
        config = None
        try:
            config = Available_Config.objects.get(category='NOTIFICATION_MESSAGE')
        except Available_Config.DoesNotExist as e:
            config = Available_Config()
            config.category = 'NOTIFICATION_MESSAGE'
        config.value = options['message']
        config.save()
        print 'Notification Message set as -' + config.value