from django.core.management.base import BaseCommand, CommandError
from lotto.models import *
from lotto.views import *
import os
import datetime
import random

class Command(BaseCommand):
    help = 'Draw the lottery and send out emails with the --email flag'

    def add_arguments(self, parser):
        parser.add_argument('--email', dest='email', action='store_true')
        parser.set_defaults(feature=False)

    def handle(self, *args, **options):

        def draw(tickets):
            n_tickets = len(tickets)

            if n_tickets < 6:
                g_size=2
            elif n_tickets < 12:
                g_size= 3
            else:
                g_size = 4
            n_groups = n_tickets//g_size
            remainder = n_tickets % g_size
            if g_size==4:
                remainder=0
                n_groups+=1
            groups = [[] for x in range(n_groups)]
            for t in tickets:
                drawing = True
                while drawing:
                    g = random.randint(1,n_groups)-1
                    if len(groups[g])<g_size+remainder:
                        drawing=False
                groups[g].append(t)

            return groups

        today = datetime.date.today()
        tickets = Ticket.objects.filter(
            draw_date=today
        ).values_list('user_id',flat=True)

        if len(tickets) < 2:
            if len(tickets)==1:
                user = User.objects.get(pk=tickets[0])
                emessage = EmailMessage(
                    subject = 'MCC lunch lottery',
                    body = f'Dear {user.first_name},\nI\'m sorry but there were not enough entries to draw the lottery today',
                    from_email = "lottery@mcc-berlin.net",
                    to = [user.email],
                    cc = ['callaghan@mcc-berlin.net']
                )

                s = emessage.send()

            return



        for i in range(100):
            groups = draw(tickets)
            if min([len(g) for g in groups])>1:
                break
            if i==99:
                return "Couldn't find a solution without a person on their own"


        for group in groups:
            users = User.objects.filter(pk__in=group)
            names = list(users.values_list('first_name', flat=True))
            namelist = f"{', '.join(names[:-1])} and {names[-1]}"

            emails = list(users.values_list('email',flat=True))

            message = f'Dear {namelist},\nYou have been selected to have lunch together today.\nGuten Appetit!'

            emessage = EmailMessage(
                subject = 'MCC lunch lottery',
                body = message,
                from_email = 'lottery@mcc-berlin.net',
                to = emails,
                cc = ['callaghan@mcc-berlin.net'],
            )
            s = emessage.send()
            time.sleep(10 + random.randrange(1,50,1)/10)



        pass
