# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError, transaction

from server.models import User, Card

import json, os, sys, inspect

def PrintFrame():
  callerframerecord = inspect.stack()[1]    # 0 represents this line
                                            # 1 represents line at caller
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  print("%s:%s, %d" % (info.filename, info.function, info.lineno))

class Command(BaseCommand):
  args = '<path/to/carddb.json>'
  help = 'Sync the carddb json file'

  def handle(self, *args, **options):
    if len(args) != 1:
      raise CommandError('need the path to the carddb.json file')

    path = args[0]
    if not os.path.exists(args[0]):
      raise CommandError('Can\'t find %s' % (path))

    fh = open(path, 'r')
    for u in json.load(fh):
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
                print("for %s, card id %s is too long" % (eu, c))
            except DataError as e:
              print(u)
              print(e)
              print("error adding new card for %s, card too long? %s" % (eu, c))
        eu.save()
      else:
        with transaction.atomic():
          nu = User(id=int(u['id']), name=u['nick'], subscribed=u['subscribed'])
          try:
            nu.save()
          except Exception as e:
            print("blah.")
            print(e, type(e))
            print(u)
          for c in u['cards']:
            try:
              # the card already exist?
              ec = Card.objects.get(card_id=c)
              # bother, it does.
              # Which of the 2 users is subscribed?
              if not u['subscribed']:
                print("skipping card %s, it's already in the db and this user is not subscribed" % (c,))
                continue
              else:
                # darn, maybe the other user is not subscribed?
                if not ec.user.subscribed:
                  print("card %s is already in the db for %s, but they are not subscribed so i'm deleting the card" % (c, ec.user))
                  ec.delete()
                else:
                  print("panic: card id %s is in use by 2 users: %s and %s" % (c, ec.user, nu))
            except ObjectDoesNotExist:
              pass
            except Exception as e:
              print(u)
              print("lol wtf", e)
            try:
              if len(c) <= 14:
                co = Card(card_id=c, user=nu)
                co.save()
              else:
                print("for %s, card id %s is too long" % (nu, c))
            except Exception as e:
              print(e, type(e))
              PrintFrame()
              print(u)
              print(nu)
              continue
          try:
            nu.save()
          except Exception as e:
            print(e, type(e))
            PrintFrame()
            print(u)
            print(nu)
    fh.close()
