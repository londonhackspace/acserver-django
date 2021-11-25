from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from server.models import Tool, Permission, Log, User

import json
import os
import sys
import datetime
import pytz


class Command(BaseCommand):
    help = 'import a json dump of the php acserver\'s db, if you specify a toolid, only that tool will be imported'

    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('toolid', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        path = options['path']
        if not os.path.exists(path):
            raise CommandError('Can\'t find %s' % (path))

        # you can just import a single tool from the json file
        # good for just importing the 3-in-1 lathe from babbage for example
        onlytool = None

        if 'toolid' in options:
            try:
                onlytool = options['toolid']
            except Exception as e:
                raise CommandError('not a tool id? %s : %s' %
                                   (options['toolid'], e))

        fh = open(path, 'r')
        j = json.load(fh)

        if len(j) != 3:
            raise CommandError(
                'The json file should have 3 top level items, not %d' % (len(j)))

        tools = j[0]
        perms = j[1]
        logs = j[2]

        for t in tools:
            # {u'status': 1, u'status_message': u'OK', u'acnode_id': 1, u'name': u'Three in One'}
            if onlytool:
                if t['acnode_id'] != onlytool:
                    continue
            tool = Tool(name=t['name'], id=t['acnode_id'],
                        status=t['status'], status_message=t['status_message'])
            tool.save()

        # format for importing dates.
        format = "%Y-%m-%dT%H:%M:%S"
        # the timestamps comes from a mysql
        # timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        # column, which uses the system timezone, which on babbage and the acserver is:
        # TZ='Europe/London'
        gmt = pytz.timezone('Europe/London')

        def check_added_by(p, out):
            added_by = None
            if p['added_by_user_id'] == None:
                # no user added this permission :/
                # lets just use user 1 (Russ), it's as good as any
                out.write(
                    "Warning: no added_by for permission %s, using user id 1" % (str(p)))
                added_by = 1
            elif p['added_by_user_id'] == 0:
                out.write(
                    "Warning: added_by for permission %s was 0, using user id 1" % (str(p)))
                added_by = 1
            else:
                added_by = p['added_by_user_id']
            return added_by

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
                ep = Permission.objects.filter(user=User.objects.get(
                    pk=p['user_id'])).get(tool_id=p['tool_id'])
                # ok, a permission already exists.
                # check in case it's been changed
                if ep.permission != int(p['permission']):
                    self.stdout.write("permission changed!")
                    self.stdout.write(str(ep))
                    self.stdout.write(str(p))
                    ep.permission = int(p['permission'])
                    ep.addedby = User.objects.get(
                        pk=check_added_by(p, self.stdout))
                    date = datetime.datetime.strptime(p['added_on'], format)
                    ep.date = gmt.localize(date)
                    ep.save()
                continue
            except ObjectDoesNotExist as e:
                # fine if it's not already in there.
                pass
            try:
                if not p['added_on']:
                    date = timezone.now()
                else:
                    date = datetime.datetime.strptime(p['added_on'], format)
                    date = gmt.localize(date)

                perm = Permission(
                    user=User.objects.get(pk=p['user_id']),
                    tool=Tool.objects.get(pk=p['tool_id']),
                    permission=int(p['permission']),
                    addedby=User.objects.get(
                        pk=check_added_by(p, self.stdout)),
                    date=date
                )
                perm.save()
            except ObjectDoesNotExist as e:
                self.stdout.write(str(p))
                self.stdout.write(
                    'Warning: User (or possibly a tool) does not exist, did you import the carddb first? (%s)' % (e))
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
            except ObjectDoesNotExist as e:
                self.stdout.write("failed to add log line: %s" % (l))

        fh.close()
