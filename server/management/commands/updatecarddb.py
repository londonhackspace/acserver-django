from django.core.management.base import BaseCommand, CommandError
from server.models import User, Card

import json, os, sys

class Command(BaseCommand):
  args = '<path/to/carddb.json>'
  help = 'Sync the carddb json file'

  def handle(self, *args, **options):
    print args
    print options

    if len(args) != 1:
      raise CommandError('need the path to the carddb.json file')
    
    path = args[0]
    if not os.path.exists(args[0]):
      raise CommandError('Can\'t find %s' % (path))

    fh = open(path, 'r')
    print fh
    for u in json.load(fh):
      # {u'perms': [], u'subscribed': False, u'gladosfile': u'zz', u'nick': u'notsubscribed', u'cards': [u'44444444'], u'id': u'4'}
      # XXX subscribed
      nu = User(id=int(u['id']), name=u['nick'], subscribed=u['subscribed'])
      for c in u['cards']:
        nu.card_set.add(Card(card_id=c))
      print nu
      print nu.card_set.all()
      nu.save()
    fh.close()

#    for poll_id in args:
#      try:
#        poll = Poll.objects.get(pk=int(poll_id))
#      except Poll.DoesNotExist:
#        raise CommandError('Poll "%s" does not exist' % poll_id)

#      poll.opened = False
#      poll.save()

#      self.stdout.write('Successfully closed poll "%s"' % poll_id)
