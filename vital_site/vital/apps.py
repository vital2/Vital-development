from __future__ import unicode_literals

from django.apps import AppConfig


class VitalConfig(AppConfig):
    name = 'vital'

    def ready(self):
        import vital.signals
