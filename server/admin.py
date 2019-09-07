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

def is_user_a_tool_maintainer(request):
  po = Permission.objects.filter(permission=2, user_id=get_logged_in_user(request).id)
  return po.count() > 0 or request.user.is_superuser

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
      # allow maintainers to see the tool table
      return is_user_a_tool_maintainer(request)

    # is this user a maintainer on the given tool?
    userpermission = obj.permissions.filter(user_id=get_logged_in_user(request).id)
    if (userpermission.count() > 0) and (userpermission.get().permission == 2):
      return True

    # otherwise, defer to the base
    return super().has_change_permission(request, obj)

  def has_module_permission(self, request):
    if not request.user.is_authenticated:
      return super().has_module_permission(request)
    return is_user_a_tool_maintainer(request)

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

  def has_module_permission(self, request):
    if not request.user.is_authenticated:
      return super().has_module_permission(request)
    return is_user_a_tool_maintainer(request)

  def has_change_permission(self, request, obj=None):
    if obj is None:
      return is_user_a_tool_maintainer(request)

    # is this user a maintainer on the tool this permission refers to?
    userpermission = obj.tool.permissions.filter(user_id=get_logged_in_user(request).id)
    if (userpermission.count() > 0) and (userpermission.get().permission == 2):
      # users cannot edit their own permissions (unless a superuser)
      # this is actually to prevent users locking themselves out
      if obj.user_id == get_logged_in_user(request).id:
        return request.user.is_superuser
      return True

    # otherwise, defer to the base
    return super().has_change_permission(request, obj)

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    # allow the user to select only tools they are a maintainer of
    if db_field.name == "tool" and not request.user.is_superuser:
      kwargs["queryset"] = Tool.objects.filter(permissions__permission=2, permissions__user_id=get_logged_in_user(request).id)

    return super().formfield_for_foreignkey(db_field, request, **kwargs)

  def has_view_permission(self, request, obj=None):
    if obj is None:
      return is_user_a_tool_maintainer(request)

    # is this user a maintainer on the tool this permission refers to?
    userpermission = obj.tool.permissions.filter(user_id=get_logged_in_user(request).id)
    if (userpermission.count() > 0) and (userpermission.get().permission == 2):
      return True

    # otherwise, defer to the base
    return super().has_view_permission(request, obj)

  def has_add_permission(self, request):
    return is_user_a_tool_maintainer(request)

  def get_queryset(self, request):
    qs = super().get_queryset(request)
    # if a superuser, return the lot
    if request.user.is_superuser:
      return qs

    # otherwise return tools where this user is a maintainer
    return qs.filter(tool__permissions__permission=2, tool__permissions__user_id=get_logged_in_user(request).id)

class LogAdmin(admin.ModelAdmin):
  fields = (('tool', 'user', 'date', 'message'),)
  list_display = ('tool', username_and_profile, 'date', 'message')
  list_filter = ('tool',)
  readonly_fields = ('tool', 'user', 'date', 'message')
  search_fields = ('user__name',)

  def has_module_permission(self, request):
    if not request.user.is_authenticated:
      return super().has_module_permission(request)
    return is_user_a_tool_maintainer(request)

  def has_view_permission(self, request, obj=None):
    if obj is None:
      return is_user_a_tool_maintainer(request)

    # is this user a maintainer on the tool this permission refers to?
    userpermission = obj.tool.permissions.filter(user_id=get_logged_in_user(request).id)
    if (userpermission.count() > 0) and (userpermission.get().permission == 2):
      return True

    # otherwise, defer to the base
    return super().has_view_permission(request, obj)

  def get_queryset(self, request):
    qs = super().get_queryset(request)
    # if a superuser, return the lot
    if request.user.is_superuser:
      return qs

    # otherwise return tools where this user is a maintainer
    return qs.filter(tool__permissions__permission=2, tool__permissions__user_id=get_logged_in_user(request).id)

# we don't want to use the Django User object in the admin
# substitute it with our own
admin.site.unregister(DJUser)
admin.site.register(DJACUser, DJUserAdmin)

admin.site.register(Tool, ToolAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Log, LogAdmin)
