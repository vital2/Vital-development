from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        config = None
        try:
            config = Available_Config.objects.get(category='NOTIFICATION_MESSAGE')
            config.delete()
        except Available_Config.DoesNotExist as e:
            pass
        print 'Notification Message removed!'
