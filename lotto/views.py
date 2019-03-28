from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import datetime
from .models import *
from .forms import *
from django.core import serializers
from django.core.mail import send_mail, EmailMessage
import time

import math, random
# Create your views here.

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)

def index(request):

    tid = 0
    template = loader.get_template('lotto/index.html')

    today = datetime.date.today().isocalendar()
    nextweek = iso_to_gregorian(today[0],today[1]+1,1)
    kw = today[1]
    y = today[0]

    enter = "Enter"

    if request.method == 'POST':
    # create a form instance and populate it with data from the request:
        form = TicketForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            try:
                ticket = Ticket.objects.get(
                    email=form.cleaned_data['email'],
                    kw=kw,
                    year=y
                )
            except:
                ticket = Ticket(
                    email=form.cleaned_data['email'],
                    kw=kw,
                    year=y
                )
            ticket.name=form.cleaned_data['name']
            ticket.availability=form.cleaned_data['availability']


            ticket.save()
            tid = ticket.id

            enter = "Thank you for entering"
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #form.save()

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TicketForm()

    tickets = Ticket.objects.filter(kw=kw,year=y)

    nodes = serializers.serialize("json", tickets)

    context = {
        'form':form,
        'nodes': nodes,
        'nextweek': nextweek,
        'tid': tid,
        'enter': enter
    }
    return HttpResponse(template.render(context, request))

def draw():
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
        print("oh dear, I didn't find a solution")
    else:
        solution = random.sample(solutions,1)[0]

        for group in solution:
            tickets = Ticket.objects.filter(
                pk__in=group['members']
            )
            days = [x[1] for x in Ticket.DAYS if x[0] in group['days']]
            emails = list(tickets.values_list('email',flat=True))
            message = 'Dear colleagues,\nYou have been selected to have lunch together on {}. The outcome was one of {} possible outcomes.\nGuten Appetit'.format(' OR '.join(days), len(solutions))

            print(emails)
            print(message)


            emessage = EmailMessage(
                subject = 'MCC lunch lottery',
                body = message,
                from_email = 'nets@mcc-berlin.net',
                to = emails,
                cc = ['callaghan@mcc-berlin.net'],
            )
            s = emessage.send()
            if s == 1:
                time.sleep(10 + random.randrange(1,50,1)/10)
