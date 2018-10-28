import os
import sys
import json
from datetime import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acserver.settings")
import django
django.setup()
from server.models import User, Tool, ToolUseTime, Permission, Log
from django.db import transaction

# A script to import json files expored from the old ACServer database
# Very much intended as a one-time importer

tools_map = {
    5 : 5, # lasercutter
    4 : 6, # biolab
    3 : 3, # Hull
    16 : 4, # Crump
}

permissions = []
usetimes = []
logs = []

if len(sys.argv) != 4:
    print("Usage: restoredump.py <permissions.json path> <usetimes.json path> <logs.json path>")
    exit(-1)

with open(sys.argv[1],'r') as f:
    permissions = json.load(f)
    print("Loaded %d permission entries" % (len(permissions),))

with open(sys.argv[2],'r') as f:
    usetimes = json.load(f)
    print("Loaded %d use entries" % (len(usetimes),))

with open(sys.argv[3],'r') as f:
    logs = json.load(f)
    print("Loaded %d log entries" % (len(logs),))

with transaction.atomic():
    # permissions
    for permission in permissions:
        if not int(permission["tool"]) in tools_map:
            print("Skipping unmapped tool %d" % int(permission["tool"]))
            continue
        try:
            current = Permission.objects.get(user=int(permission["user"]),
                tool=tools_map[int(permission["tool"])])
            if int(current.permission) < int(permission["permission"]):
                print("Upgrading user %d to %d" % (int(permission["user"]), int(permission["permission"])))
                current.permission = int(permission["permission"])
                current.save()
        except:
            # existing perm not existing. Add it.
            user = None
            try:
                user = User.objects.get(id=int(permission["user"]))
            except:
                print("User %d does not exist - skipping" % (int(permission["user"]),))
                continue
            addedby = User.objects.get(id=int(permission["addedby"]))
            tool = Tool.objects.get(id=tools_map[int(permission["tool"])])
            current = Permission(user=user, permission=int(permission["permission"]),
                        addedby=addedby, date=datetime.utcfromtimestamp(int(permission["date"])), 
                        tool=tool)
            current.save()
            print("Adding permission for user %d" % (int(permission["user"]),))

    # logs
    for log in logs:
        if not int(log["tool"]) in tools_map:
            print("Skipping unmapped tool %d" % int(log["tool"]))
            continue
        user = None
        try:
            user = User.objects.get(id=int(log["user"]))
        except:
            print("User %d does not exist - skipping" % (int(log["user"]),))
            continue
        tool = Tool.objects.get(id=tools_map[int(log["tool"])])
        l = Log(user=user, tool=tool, message=log["message"], time=int(log["time"]),
            date=datetime.utcfromtimestamp(int(log["date"])))
        l.save()

