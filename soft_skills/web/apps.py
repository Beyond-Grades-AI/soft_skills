from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        from language_model import ScheduleEvaluation
        ScheduleEvaluation.start()
