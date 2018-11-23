from django.core.management.base import BaseCommand, CommandError
from lotto.models import *
from lotto.views import *
import os

class Command(BaseCommand):
    help = 'Draw the lottery and send out emails with the --email flag'

    def add_arguments(self, parser):
        parser.add_argument('--email', dest='email', action='store_true')
        parser.set_defaults(feature=False)

    def handle(self, *args, **options):

        def comma_separator(sequence, conjunction="and"):
            if len(sequence) > 1:
                sequence = list(sequence)
                return '{} {} {}'.format(
                    ', '.join(sequence[:-1]),
                    conjunction,
                    sequence[-1]
                    )
            try:
                return sequence[0]
            except IndexError:
                raise ValueError('Must pass in at least one element')

        email = options['email']
        today = datetime.date.today().isocalendar()
        #today = datetime.date(2018,5,14).isocalendar()
        lastweek = iso_to_gregorian(today[0],today[1]-1,1).isocalendar()
        kw = lastweek[1]
        y = today[0]

        tickets = Ticket.objects.filter(
            kw=kw,
            year=y
        )

        GROUP_SIZE = 4
        MIN_SIZE = 2

        ngroups = math.ceil(tickets.count()/GROUP_SIZE)

        solutions = []
        max_iter = 500
        for i in range(max_iter):
            # Set up some empty groups
            groups = []
            for i in range(ngroups):
                groups.append({
                    'days': set(),
                    'members': set()
                })

            nogroup = set(tickets.values_list('id',flat=True))
            no_solution=False
            # Choose a random ticket to populate each group
            tids = random.sample(nogroup,ngroups)
            for g, tid in enumerate(tids):
                groups[g]['members'].add(tid)
                nogroup.remove(tid)
                t = Ticket.objects.get(pk=tid)
                groups[g]['days'].update(t.availability)
            # add the remaining tickets to a random group they can fit into
            for tid in random.sample(nogroup,len(nogroup)):
                t = Ticket.objects.get(pk=tid)
                pos_groups = [i for i, x in enumerate(groups) if len(x['days'].intersection(t.availability))>0 and len(x['members'])<GROUP_SIZE]
                # No possible solutions, we'll have to start again!
                if len(pos_groups)==0:
                    no_solution=True
                    break
                g = random.sample(pos_groups,1)[0]
                groups[g]['members'].add(tid)
                nogroup.remove(tid)
                groups[g]['days'] = groups[g]['days'].intersection(t.availability)
            for g in groups:
                if len(g['members']) < MIN_SIZE:
                    no_solution=True
            if no_solution==False:
                if groups not in solutions:
                    solutions.append(groups)

        if len(solutions)==0:
            persons = comma_separator(tickets.values_list(
                'name',flat=True
            ))
            emails = list(tickets.values_list('email',flat=True))
            message = 'Dear {},\nI\'m really sorry, but we couldn\'t find a solution that satisfied all your availabilities, but you are welcome to try to organise a lunch between yourselves'.format(
                persons,
            )
            print(emails)
            print(message)
            emessage = EmailMessage(
                subject = 'MCC lunch lottery',
                body = message,
                from_email = 'nets@mcc-berlin.net',
                to = emails,
                cc = ['callaghan@mcc-berlin.net'],
            )
            if email:
                print("Emailing this group")
                s = emessage.send()
                #s = 0
                if s == 1:
                    time.sleep(10 + random.randrange(1,50,1)/10)
            else:
                print("Not emailing this group")
        else:
            solution = random.sample(solutions,1)[0]

            for group in solution:
                tickets = Ticket.objects.filter(
                    pk__in=group['members']
                )
                persons = comma_separator(tickets.values_list(
                    'name',flat=True
                ))
                days = [x[1] for x in Ticket.DAYS if x[0] in group['days']]
                emails = list(tickets.values_list('email',flat=True))
                message = 'Dear {},\nYou have been selected to have lunch together on {}. The outcome was one of {} possible outcomes.\nGuten Appetit'.format(
                    persons,
                    #' OR '.join(days),
                    comma_separator(days, "or"),
                    len(solutions)
                )

                print(emails)
                print(message)


                emessage = EmailMessage(
                    subject = 'MCC lunch lottery',
                    body = message,
                    from_email = 'nets@mcc-berlin.net',
                    to = emails,
                    cc = ['callaghan@mcc-berlin.net'],
                )
                if email:
                    print("Emailing this group")
                    s = emessage.send()
                    #s = 0
                    if s == 1:
                        time.sleep(10 + random.randrange(1,50,1)/10)
                else:
                    print("Not emailing this group")
