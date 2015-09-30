from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from server.models import User, Card

import json, os, sys

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
            eu.card_set.add(Card(card_id=c))
        eu.save()
      else:
        nu = User(id=int(u['id']), name=u['nick'], subscribed=u['subscribed'])
        for c in u['cards']:
          nu.card_set.add(Card(card_id=c))
        nu.save()
    fh.close()
