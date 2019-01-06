# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError, transaction

from server.models import User, Card

import json, os, sys, inspect, stat

def PrintFrame():
  callerframerecord = inspect.stack()[1]    # 0 represents this line
                                            # 1 represents line at caller
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  print("%s:%s, %d" % (info.filename, info.function, info.lineno))

class Command(BaseCommand):
  help = 'Sync the carddb json file'

  def add_arguments(self, parser):
        parser.add_argument('path')

  def handle(self, *args, **options):
    path = options['path']
    if not os.path.exists(path):
      raise CommandError('Can\'t find %s' % (path))

    sr = os.stat(path)
    if sr[stat.ST_SIZE] == 0:
      raise CommandError('%s is zero size, not using it.' % (path))

    fh = open(path, 'r')
    jdata = json.load(fh)
    fh.close()

    if len(jdata) == 0:
      raise CommandError('%s has no entries, not using it.' % (path))

    for u in jdata:
      # {u'perms': [], u'subscribed': False, u'gladosfile': u'zz', u'nick': u'notsubscribed', u'cards': [u'44444444'], u'id': u'4'}
      eu = None
      try:
        eu = User.objects.get(pk=u['id'])
      except ObjectDoesNotExist:
        pass
      if eu:
        # update nick and subscription
        eu.name = u['nick']
        eu.subscribed=u['subscribed']
        #gladosfile should be empty rather than null in this DB
        if u['gladosfile'] is not None:
          eu.gladosfile=u['gladosfile']
        else:
          eu.gladosfile=""
        ecs = eu.card_set.all()
        for ec in ecs:
          # delete cards that have gone away
          if ec.card_id not in u['cards']:
            ec.delete()
        for c in u['cards']:
          # add new cards
          if c not in [x.card_id for x in ecs]:
            try:
              if len(c) <= 14:
                co = Card(card_id=c, user=eu)
                co.save()
              else:
                self.stdout.write("for %s, card id %s is too long" % (eu, c))
            except DataError as e:
              self.stdout.write(u)
              self.stdout.write(e)
              self.stdout.write("error adding new card for %s, card too long? %s" % (eu, c))
        eu.save()
      else:
        with transaction.atomic():
          nu = User(id=int(u['id']), name=u['nick'], subscribed=u['subscribed'])
          #gladosfile should be empty rather than null in this DB
          if u['gladosfile'] is not None:
            nu.gladosfile = u['gladosfile']
          try:
            nu.save()
          except Exception as e:
            self.stdout.write("blah.")
            self.stdout.write(e, type(e))
            self.stdout.write(u)
          for c in u['cards']:
            try:
              # the card already exist?
              ec = Card.objects.get(card_id=c)
              # bother, it does.
              # Which of the 2 users is subscribed?
              if not u['subscribed']:
                self.stdout.write("skipping card %s, it's already in the db and this user is not subscribed" % (c,))
                continue
              else:
                # darn, maybe the other user is not subscribed?
                if not ec.user.subscribed:
                  self.stdout.write("card %s is already in the db for %s, but they are not subscribed so i'm deleting the card" % (c, ec.user))
                  ec.delete()
                else:
                  self.stdout.write("panic: card id %s is in use by 2 users: %s and %s" % (c, ec.user, nu))
            except ObjectDoesNotExist:
              pass
            except Exception as e:
              self.stdout.write(u)
              self.stdout.write("lol wtf", e)
            try:
              if len(c) <= 14:
                co = Card(card_id=c, user=nu)
                co.save()
              else:
                self.stdout.write("for %s, card id %s is too long" % (nu, c))
            except Exception as e:
              self.stdout.write(e, type(e))
              PrintFrame()
              self.stdout.write(u)
              self.stdout.write(nu)
              continue
          try:
            nu.save()
          except Exception as e:
            self.stdout.write(e, type(e))
            PrintFrame()
            self.stdout.write(u)
            self.stdout.write(nu)

    carddb_by_id = {}
    for u in jdata:
      # {u'perms': [], u'subscribed': False, u'gladosfile': u'zz', u'nick': u'notsubscribed', u'cards': [u'44444444'], u'id': u'4'}
      carddb_by_id[int(u['id'])] = u

    # loop through all acnode users and check that they exist in the carddb.
    for au in User.objects.all():
      if au.id not in carddb_by_id:
        self.stdout.write("user with id %d is in the local db, but not in carddb.json, unsubscribeing them and removing their cards" % (au.id))
        # remove  cards
        cs = au.card_set.all()
        for c in cs:
            c.delete()
        # set status to unsubscribed
        au.subscribed = False
        # we don't want to delete them cos of 'on cascade delete' stuffs, and there account might get re-activated
        au.save()
