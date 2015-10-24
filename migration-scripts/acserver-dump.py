#!/usr/bin/env python
#
# import tools, acnodes, permissions and toolusage from the old acserver
#

import MySQLdb, json, sys, os, datetime, time

if len(sys.argv) != 2:
  print "usage: %s <password>"
  sys.exit(-1)

db = MySQLdb.connect(host="localhost",
                           user="acserver",
                           passwd=sys.argv[1],
                           db="acserver")

cur = db.cursor()

def datetime_handler(obj):
  if type(obj) == datetime.datetime:
    return obj.isoformat()
  elif type(obj) == datetime.date:
    return obj.isoformat()
  else:
    raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def select_to_json(sql):
  out = []
  cur.execute(sql)
  cols = []
  for i in cur.description:
    cols.append(i[0])

  for row in cur:
    r = {}
    for i,k in enumerate(cols):
        r[k] = row[i]
    out.append(r)
    
  return out

out = []

# acnode_id is the one we want
r = select_to_json("SELECT ac.acnode_id, t.name, t.status, t.status_message FROM "
          "acnodes ac, tools t "
          "WHERE ac.tool_id=t.tool_id;")

out.append(r)

#tool_id | user_id | last_used | added_by_user_id | added_on            | permission
r = select_to_json("SELECT * from permissions")

out.append(r)

r = select_to_json("SELECT tool_id, user_id, logged_at, logged_event, time from toolusage")

out.append(r)
                           
db.close()

print json.dumps(out, default=datetime_handler)
