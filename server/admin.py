from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.admin import UserAdmin as DJUserAdmin
from django.contrib.auth.models import User as DJUser

from .models import Tool, User, Card, Permission, Log, DJACUser

import logging

logger = logging.getLogger('django.request')

def username_and_profile(u):
  if u.__class__ == Permission or u.__class__ == Card or u.__class__ == Log:
    u = u.user
  return format_html('<a href="https://london.hackspace.org.uk/members/profile.php?id={}">{}</a>', u.id, u.name)
username_and_profile.short_description = 'Name'
username_and_profile.admin_order_field = 'user'

def get_logged_in_user(request):
  # gets a user by either LDAP or local user ID
  if hasattr(request.user,'ldap_user'):
    # if so get the ldap uid and subtract 100000 to get the
    # lhs user id, and then get the associated carddb user thing.
    user = User.objects.get(id = int(request.user.ldap_user.attrs['uidnumber'][0]) - 100000)
  else:
    # not an ldap user - this will be local testing
    try:
      user = User.objects.get(id=request.user.id)
    except ObjectDoesNotExist:
      # darn, the user logged into the admin interface
      # does not have a correspoinding carddb user...
      # since this won't be used on the live site
      # lets just try uid 1
      user = User.objects.get(id=1)
      logger.critical('Can\'t find carddb user for django user %d, using user id 1 instead', request.user.id)
  return user

class ToolAdmin(admin.ModelAdmin):
  readonly_fields = ('inuse', 'inuseby')
  list_display = ('id', 'name', 'status', 'status_message', 'secret', 'inuse', 'inuseby', 'type')
  search_fields = ('name','id')
  list_editable = ('status', 'status_message', 'type')
  list_filter = ('status', 'type')

  def get_queryset(self, request):
    qs = super().get_queryset(request)
    # if a superuser, return the lot
    if request.user.is_superuser:
      return qs

    # otherwise return tools where this user is a maintainer
    return qs.filter(permissions__permission=2, permissions__user_id=get_logged_in_user(request).id)


  def has_change_permission(self, request, obj=None):
    if obj is None:
      # allow users to see the tool table, even if they can't see the specific entry
      return True

    # is this user a maintainer on the given tool?
    userpermission = obj.permissions.filter(user_id=request.user.id)
    if (userpermission.count() > 0) and (userpermission.get().permission == 2):
      return True

    # otherwise, defer to the base
    return super().has_change_permission(request, obj)

class UserAdmin(admin.ModelAdmin):
  fields = (('lhsid', 'name', 'subscribed', 'gladosfile'),)
  readonly_fields = ('lhsid', 'name', 'subscribed')
  list_display = ('id', 'lhsid', 'username_and_profile', 'subscribed',)
  search_fields = ('name','id')
  list_filter = ('subscribed',)

class CardAdmin(admin.ModelAdmin):
  fields = (('user', 'card_id'),)
  readonly_fields = ('user', 'card_id')
  list_display = ('card_id', username_and_profile,)

class PermissionAdmin(admin.ModelAdmin):
  fields = (('tool', 'user', 'permission'),)
  list_display = ('tool', username_and_profile, 'permission', 'addedby', 'date')
  list_filter = ('tool', 'permission')

  def save_model(self, request, obj, form, change):
    # are we running with an ldap backend?
    user = get_logged_in_user(request)
    obj.addedby = user
    obj.save()

class LogAdmin(admin.ModelAdmin):
  fields = (('tool', 'user', 'date', 'message'),)
  list_display = ('tool', username_and_profile, 'date', 'message')
  list_filter = ('tool',)
  readonly_fields = ('tool', 'user', 'date', 'message')
  search_fields = ('user__name',)

# we don't want to use the Django User object in the admin
# substitute it with our own
admin.site.unregister(DJUser)
admin.site.register(DJACUser, DJUserAdmin)

admin.site.register(Tool, ToolAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Log, LogAdmin)
