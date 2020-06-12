from django.core.management import call_command
from django_cron import CronJobBase, Schedule


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=0)
    code = 'login.my_cron_job'

    def do(self):
        call_command('flushexpiredtokens')

