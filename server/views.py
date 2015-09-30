from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseForbidden
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.decorators import available_attrs


from models import Tool, Card, User, Permissions, ToolUseTime

import json, logging
from functools import wraps

logger = logging.getLogger('django.request')

@require_GET
def status(request, tool_id):
  try:
    t = Tool.objects.get(pk=tool_id)
  except ObjectDoesNotExist, e:
    return HttpResponse('-1', content_type='text/plain')

  return HttpResponse(str(t.status), content_type='text/plain')

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
    perm = c.user.permissions_set.get(tool=t).permission
  except ObjectDoesNotExist, e:
    perm = 0

  if not c.user.subscribed:
    # log unsubscribed user tried to use tool.
    perm = -1

  return HttpResponse(str(perm), content_type='text/plain')

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

  bcp = bc.user.permissions_set.get(tool=t).get_permission_display()
  if bcp != 'maintainer':
    return HttpResponse(str(0), content_type='text/plain')

  if not tc.user.subscribed:
    # needs to be subscribed to be a user
    return HttpResponse(str(0), content_type='text/plain')
  
  np = Permissions(user=tc.user, permission=1, tool=t)
  np.save()

  return HttpResponse(str(1), content_type='text/plain')

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
    cp = c.user.permissions_set.get(tool=t).get_permission_display()
    if cp != 'maintainer':
      return HttpResponse(str(0), content_type='text/plain')

  t.status = status
  t.save()
  
  return HttpResponse(str(1), content_type='text/plain')

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
  if status == 1:
    t.inuseby = c.user
  else:
    t.inuseby = None
  t.inuse = status
  t.save()

  return HttpResponse('1', content_type='text/plain')

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

  tut = ToolUseTime(tool=t, inuseby=c.user, duration=int(duration))
  tut.save()
  
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
    perm = 'un-authorised'
    if u:
      try:
        perm = u.permissions_set.get(tool=t).get_permission_display()
      except ObjectDoesNotExist:
        pass
    ret.append({'name': t.name, 'status': t.get_status_display(), 'status_message' : t.status_message, 'in_use' : t.get_inuse_display(), 'permission' : perm})

  return HttpResponse(json.dumps(ret), content_type='text/plain')
