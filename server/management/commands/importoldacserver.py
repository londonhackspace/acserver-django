from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from server.models import Tool, Permissions, Log, User

import json, os, sys, datetime, pytz

class Command(BaseCommand):
  args = '<path/to/dump.json> [toolid]'
  help = 'import a json dump of the php acserver\'s db, if you specify a toolid, only that tool will be imported'

  def handle(self, *args, **options):
    if len(args) < 1 or len(args) > 2:
      raise CommandError('need the path to the .json file and an optional toolid')
    
    path = args[0]
    if not os.path.exists(args[0]):
      raise CommandError('Can\'t find %s' % (path))

    # you can 
    onlytool = None

    if len(args) == 2:
      try:
        onlytool = int(args[1])
      except Exception, e:
        raise CommandError('not a tool id? %s : %s' % (args[1], e))

    fh = open(path, 'r')
    j = json.load(fh)

    if len(j) != 3:
      raise CommandError('The json file should have 3 top level items, not %d' % (len(j)))

    tools = j[0]
    perms = j[1]
    logs  = j[2]

    for t in tools:
      # {u'status': 1, u'status_message': u'OK', u'acnode_id': 1, u'name': u'Three in One'}
      if onlytool:
        if t['acnode_id'] != onlytool:
          continue
      tool = Tool(name=t['name'], id=t['acnode_id'], status=t['status'], status_message=t['status_message'])
      tool.save()

    # format for importing dates.
    format = "%Y-%m-%dT%H:%M:%S"
    # the timestamps comes from a mysql
    # timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    # column, which uses the system timezone, which on babbage and the acserver is:
    # TZ='Europe/London'
    gmt = pytz.timezone('Europe/London')

    for p in perms:
      # {u'last_used': None, u'user_id': 38, u'tool_id': 1, u'permission': 2, u'added_by_user_id': None, u'added_on': u'2013-05-05T02:38:47'}
      # we ignore last_used...
#      print p
      # skip if it's not the tool we want.
      if onlytool:
        if p['tool_id'] != onlytool:
          continue
      # check for existing permissions
      try:
        ep = Permissions.objects.filter(user=User.objects.get(pk=p['user_id'])).get(tool_id=p['tool_id'])
        # ok, a permission already exists.
        # check in case it's been changed
        if ep.permission != int(p['permission']):
          print "permission changed!"
          print ep
          print p
          ep.permission = int(p['permission'])
          ep.addedby = User.objects.get(pk=added_by)
          date = datetime.datetime.strptime(p['added_on'], format)
          ep.date = gmt.localize(date)
          ep.save()
        continue
      except ObjectDoesNotExist, e:
        # fine if it's not already in there.
        pass
      try:
        added_by = None
        if p['added_by_user_id'] == None:
          # no user added this permission :/
          # lets just use user 1 (Russ), it's as good as any
          print "Warning: no added_by for permission %s" % (str(p))
          added_by = 1
        else:
          added_by = p['added_by_user_id']
        date = datetime.datetime.strptime(p['added_on'], format)
        date = gmt.localize(date)
        perm = Permissions(
          user=User.objects.get(pk=p['user_id']),
          tool=Tool.objects.get(pk=p['tool_id']),
          permission = int(p['permission']),
          addedby = User.objects.get(pk=added_by),
          date = date
          )
        perm.save()
      except ObjectDoesNotExist, e:
        print p
        print 'Warning: User (or possibly a tool) does not exist, did you import the carddb first? (%s)' % (e)      
#        raise CommandError()

    for l in logs:
      # skip if it's not the tool we want.
      if onlytool:
        if l['tool_id'] != onlytool:
          continue
      # {u'tool_id': 1, u'logged_at': u'2013-05-16T19:57:59', u'user_id': 38, u'logged_event': u'Access Finished', u'time': 0}
      try:
        date = datetime.datetime.strptime(l['logged_at'], format)
        date = gmt.localize(date)
        l = Log(tool=Tool.objects.get(pk=l['tool_id']), user=User.objects.get(pk=l['user_id']),
                date=date,
                message=l['logged_event'], time=l['time'])
        l.save()
      except ObjectDoesNotExist, e:
        print "failed to add log line: %s" % (l)

    fh.close()
