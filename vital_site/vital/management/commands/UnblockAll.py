# from django.core.management.base import BaseCommand, CommandError
# from vital.models import VLAB_User, Blocked_User
# from django.core.mail import send_mail
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# class Command(BaseCommand):
#
#     help = "DEPRECATED : Command to unblock all blocked users"
#
#     def handle(self, *args, **options):
#         logger.debug("Unblocking all users")
#         blocked_users = Blocked_User.objects.all()
#         for blocked in blocked_users:
#             user = VLAB_User.objects.get(id=blocked.user_id)
#             logger.debug('Generating re-activation mail for '+user.email)
#             send_mail('Activation mail', 'Hi ' + user.first_name + ',\r\n\n Welcome back to Vital. '
#                                                                    'Please use activation code : ' +
#                       str(user.activation_code) + ' for re-activating your account.\r\n\nVital',
#                       'no-reply-vital@nyu.edu', [user.email], fail_silently=False)
#             blocked.delete()
