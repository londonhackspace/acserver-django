from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.decorators import available_attrs
from django.db.models import Sum

from models import Tool, Card, User, Permission, ToolUseTime, Log

import json, logging, datetime
from netaddr import IPAddress, IPNetwork
from functools import wraps
from pytz import timezone

logger = logging.getLogger('django.request')

def check_secret(func):
  def _decorator(func):
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
      try:
        tool = Tool.objects.get(pk=kwargs['tool_id'])
      except ObjectDoesNotExist, e:
        return func(request, *args, **kwargs)
      if tool.secret != None and tool.secret != "":
        if 'HTTP_X_AC_KEY' not in request.META:
          # the tool has a secret, but it's wasn't sent
          # so just fail it.
          logger.critical('Missing secret key for tool %d // %s from %s', tool.id, request.path, request.META['REMOTE_ADDR'],
                    extra={
                        'status_code': 200,
                        'request': request
                    }
                )
          return HttpResponse('0', content_type='text/plain')

        if tool.secret != request.META['HTTP_X_AC_KEY']:
          logger.critical('Wrong secret key for tool %d // %s from %s', tool.id, request.path, request.META['REMOTE_ADDR'],
                    extra={
                        'status_code': 200,
                        'request': request
                    }
                )
          return HttpResponse('0', content_type='text/plain')
      else:
        if 'HTTP_X_AC_KEY' in request.META:
          # N.B. this allows acnodes to send a secret if we don't have one.
          logger.warning('tool %d sent a secret key, but we don\'t have one for it! // %s from %s', tool.id, request.path, request.META['REMOTE_ADDR'],
                    extra={
                        'status_code': 200,
                        'request': request
                    }
                )
      return func(request, *args, **kwargs)
    return inner
  return _decorator(func)

def check_ip(func):
  def _decorator(func):
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
      if IPAddress(request.META['REMOTE_ADDR']) not in IPNetwork(settings.ACNODE_IP_RANGE):
        logger.warning('invalid access attempt from %s', request.META['REMOTE_ADDR'],
                    extra={
                        'status_code': 403,
                        'request': request
                    }
              )
        return HttpResponse('IP forbidden\n', status=403, content_type='text/plain')
      return func(request, *args, **kwargs)
    return inner
  return _decorator(func)

@require_GET
def status(request, tool_id):
  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  return HttpResponse(str(t.status), content_type='text/plain')

@check_secret
@check_ip
@require_GET
def card(request, tool_id, card_id):

  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  try:
    c = Card.objects.get(card_id=card_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  try:
    perm = c.user.permission_set.get(tool=t).permission
  except ObjectDoesNotExist, e:
    perm = 0

  if not c.user.subscribed:
    # log unsubscribed user tried to use tool.
    perm = -1

  return HttpResponse(str(perm), content_type='text/plain')

@check_secret
@check_ip
@csrf_exempt
@require_POST
def granttocard(request, tool_id, to_cardid, by_cardid):
  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  try:
    bc = Card.objects.get(card_id=by_cardid)
  except ObjectDoesNotExist, e:
    return HttpResponse('0', content_type='text/plain')

  try:
    tc = Card.objects.get(card_id=to_cardid)
  except ObjectDoesNotExist, e:
    return HttpResponse('0', content_type='text/plain')

  try:
    bcp = bc.user.permission_set.get(tool=t).get_permission_display()
    if bcp != 'maintainer':
      return HttpResponse(str(0), content_type='text/plain')
  except ObjectDoesNotExist, e:
    return HttpResponse(str(0), content_type='text/plain')

  if not tc.user.subscribed:
    # needs to be subscribed to be a user
    return HttpResponse(str(0), content_type='text/plain')

  if not bc.user.subscribed:
    # needs to be subscribed to be a maintainer
    return HttpResponse(str(0), content_type='text/plain')

  try:
    # does the permission already exist?
    p = Permission.objects.get(user=tc.user, tool=t)
    # if so just report success.
    return HttpResponse(str(1), content_type='text/plain')
  except ObjectDoesNotExist, e:
    pass

  np = Permission(user=tc.user, permission=1, tool=t, addedby=bc.user)
  np.save()

  return HttpResponse(str(1), content_type='text/plain')

@check_secret
@check_ip
@csrf_exempt
@require_POST
def settoolstatus(request, tool_id, status, card_id):
  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  try:
    c = Card.objects.get(card_id=card_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('0', content_type='text/plain')

  status = int(status)

  if status == 1:
    # only maintainers can set a tool online
    cp = c.user.permission_set.get(tool=t).get_permission_display()
    if cp != 'maintainer':
      return HttpResponse(str(0), content_type='text/plain')

  t.status = status
  t.save()

  if status == 0:
    l = Log(tool=t, user=c.user, message="Tool taken out of service")
    l.save()
  elif status == 1:
    l = Log(tool=t, user=c.user, message="Tool put into service")
    l.save()
  
  return HttpResponse(str(1), content_type='text/plain')

@check_secret
@check_ip
@csrf_exempt
@require_POST
def settooluse(request, tool_id, status, card_id):
  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  try:
    c = Card.objects.get(card_id=card_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('0', content_type='text/plain')
  
  status = int(status)
  message = None
  if status == 1:
    t.inuseby = c.user
    message = "Access Started"
  else:
    t.inuseby = None
    message = "Access Finished"
  t.inuse = status
  t.save()

  l = Log(tool=t, user=c.user, message=message)
  l.save()

  return HttpResponse('1', content_type='text/plain')

# used by other things?
@require_GET
def isinuse(request, tool_id):
  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  if t.inuse:
    return HttpResponse('yes', content_type='text/plain')
  else:
    return HttpResponse('no', content_type='text/plain')

@check_secret
@check_ip
@csrf_exempt
@require_POST
def settoolusetime(request, tool_id, card_id, duration):
  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  try:
    c = Card.objects.get(card_id=card_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('0', content_type='text/plain')

  # should we check that the user has permissions?
  # we could be in a situation where someone is using a tool
  # and there permisson is removed while they are using it.
  # in that case we'd still want to log that the time they used...

  tut = ToolUseTime(tool=t, inuseby=c.user, duration=int(duration))
  tut.save()

  l = Log(tool=t, user=c.user, message="Tool used for %d seconds" % (int(duration),), time=int(duration))
  l.save()
  
  return HttpResponse('1', content_type='text/plain')

# api stuff from here.
class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

def require_api_key(func):  
  def _decorator(func):
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
      if 'HTTP_API_KEY' not in request.META:
        logger.warning('Missing API key for %s // %s from %s', request.method, request.path, request.META['REMOTE_ADDR'],
                    extra={
                        'status_code': 401,
                        'request': request
                    }
                )
        return HttpResponseUnauthorized("API Key required")
      if request.META['HTTP_API_KEY'] != settings.ACS_API_KEY:
        logger.warning('wrong API key: %s for %s // %s from %s', request.META['HTTP_API_KEY'], request.method, request.path, request.META['REMOTE_ADDR'],
                    extra={
                        'status_code': 401,
                        'request': request
                    }
                )
        return HttpResponseUnauthorized("HTTP Error 401: Forbidden")
      return func(request, *args, **kwargs)
    return inner
  return _decorator(func)

# settings.ACS_API_KEY
# HttpRequest.META
@require_api_key
@require_GET
def get_tools_summary_for_user(request, user_id):
  try:
    u = User.objects.get(pk=user_id)
  except ObjectDoesNotExist:
    u = None

  ret = []
  # [{u'status': u'Operational', u'permission': u'user', u'status_message': u'working ok', u'name': u'test_tool', u'in_use': u'no'}]
  for t in Tool.objects.order_by('pk'):
    perm = 'unauthorised'
    if u:
      try:
        perm = u.permission_set.get(tool=t).get_permission_display()
      except ObjectDoesNotExist:
        pass
    ret.append({'name': t.name, 'status': t.get_status_display(), 'status_message' : t.status_message, 'in_use' : t.get_inuse_display(), 'permission' : perm})

  return HttpResponse(json.dumps(ret), content_type='text/plain')


@require_api_key
@require_GET
def get_tools_status(request):
  ret = []
  # [{u'status': u'Operational', u'status_message': u'working ok', u'name': u'test_tool', u'in_use': u'no'}]
  for t in Tool.objects.order_by('pk'):
    ret.append({'name': t.name, 'status': t.get_status_display(), 'status_message' : t.status_message, 'in_use' : t.get_inuse_display()})

  return HttpResponse(json.dumps(ret), content_type='application/json')

#@require_api_key
@require_GET
def get_tool_runtime(request, tool_id, start_time):
  # start_time is a time_t
  t = Tool.objects.get(pk=int(tool_id))

  # start = datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(0,3600 * 24 * 90,0)
  # time.mktime(start.timetuple())

  # XXX timezone here should get system one, or use django settings or something :/
  start = datetime.datetime.fromtimestamp(float(start_time),timezone("Europe/London"))

  # filter out runs that lasted longer than 24 hours, see issue #5
  seconds = Log.objects.filter(tool=t).filter(date__gt=start).filter(message='Time Used').filter(time__lt=3600 * 24).aggregate(Sum('time'))['time__sum']

  if not seconds:
    seconds = 0

  #
  # solexious: 399h:56m:57s of lasing have occurred. was on the 18th of august
  #
  # colin:/tank/babbage-backup-2015/home/solexious/coolbot/ : 1798023
  # ^-- datestamp was Oct 20 01:30
  # which is 499h:27m:03s
  #
  # BUT - we don't know when it started... :(
  #
  if int(tool_id) == 5:
    # the laser cutter
    coolbot = 1798023
    seconds = seconds + coolbot

  hours = seconds / 3600
  minutes = (seconds % 3600) / 60
  seconds = (seconds % 3600) % 60

  printable = '%dh:%dm:%ds' % (hours, minutes, seconds)

  #
  # the 700 hour lifetime is right for the lasercutter here, needs to be configureable on a per tool basis
  # and updatable by maintainers.
  #
  # ... and the text here is only applicable to the lasercutter :/
  #
  verbose = printable + ' of lasing have occurred. Approximately %d hours until the tube dies.' % (2800 - hours)

  ret = []
  # {'name': name, 'seconds': secs, 'printable': 'HH:MM:SS', 'verbose': 'blah blah'}
  ret.append({'name': t.name, 'seconds' : seconds, 'printable' : printable, 'verbose': verbose})

  return HttpResponse(json.dumps(ret), content_type='application/json')




#just testing some simple UI stuff
def calheatmap1(request):
  #stufftest = {}
  #stufftest['thing'] = "test"
  return render(request, 'server/calheatmaptest.html')