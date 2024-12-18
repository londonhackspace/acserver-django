from django.db import models
from django.contrib import admin
from django.forms.widgets import TextInput
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.admin import UserAdmin as DJUserAdmin
from django.contrib.auth.models import User as DJUser

from .models import Tool, User, Card, Permission, Log, DJACUser

import logging

logger = logging.getLogger('django.request')


def username_and_profile(u):
    name = ""
    if u.__class__ == Permission or u.__class__ == Card or u.__class__ == Log:
        u = u.user
    return u.username_and_profile()
username_and_profile.short_description = 'Name'
username_and_profile.admin_order_field = 'user'

def lhs_id(u):
    if u.__class__ == Permission or u.__class__ == Card or u.__class__ == Log:
        u = u.user
    return u.lhsid()
lhs_id.admin_order_field = 'id'



def get_logged_in_user(request):
    # gets a user by either LDAP or local user ID
    if hasattr(request.user, 'ldap_user'):
        # if so get the ldap uid and subtract 100000 to get the
        # lhs user id, and then get the associated carddb user thing.
        user = User.objects.get(
            id=int(request.user.ldap_user.attrs['uidnumber'][0]) - 100000)
    else:
        # not an ldap user - this will be local testing
        try:
            user = User.objects.get(id=request.user.id)
        except ObjectDoesNotExist:
            user = DJUser.objects.get(id=request.user.id)
            logger.critical(
                'Can\'t find carddb user for django user %d, using fallback Django user instead', request.user.id)
    return user


def is_user_a_tool_maintainer(request):
    po = Permission.objects.filter(
        permission=2, user_id=get_logged_in_user(request).id)
    return po.count() > 0 or request.user.is_superuser


class ToolAdmin(admin.ModelAdmin):
    readonly_fields = ('inuse', 'inuseby')
    list_display = ('id', 'name', 'status', 'status_message',
                    'secret', 'inuse', 'inuseby', 'type', 'mqtt_name')
    search_fields = ('name', 'id')
    list_editable = ('status', 'status_message',)
    list_filter = ('status', 'type')

    formfield_overrides = {
        models.TextField: {'widget': TextInput},
    }

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
        userpermission = obj.permissions.filter(
            user_id=get_logged_in_user(request).id)
        if (userpermission.count() > 0) and (userpermission.get().permission == 2):
            return True

        # otherwise, defer to the base
        return super().has_change_permission(request, obj)

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return super().has_module_permission(request)
        return is_user_a_tool_maintainer(request)

    # allow tool admins access to view, so the autocomplete dropdowns work
    def has_view_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return super().has_view_permission(request)

        if obj is None:
            return is_user_a_tool_maintainer(request)

        # is this user a maintainer on the given tool?
        userpermission = obj.permissions.filter(
            user_id=get_logged_in_user(request).id)
        if (userpermission.count() > 0) and (userpermission.get().permission == 2):
            return True

        # otherwise, defer to the base
        return super().has_view_permission(request, obj)


class UserAdmin(admin.ModelAdmin):
    fields = (('lhsid', 'name', 'nickname', 'subscribed', 'gladosfile'),)
    readonly_fields = ('lhsid', 'name', 'nickname', 'subscribed')
    list_display = ('id', 'lhsid', 'username_and_profile', 'subscribed',)
    search_fields = ('name', 'nickname', 'id')
    list_filter = ('subscribed',)
    
    # allow tool admins access to view, so the autocomplete dropdowns work
    def has_view_permission(self, request, obj=None):
        return is_user_a_tool_maintainer(request)

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.id == 0:
            return False
        return super().has_change_permission(request,obj)
    
    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.id == 0:
            return False
        return super().has_delete_permission(request,obj)


class CardAdmin(admin.ModelAdmin):
    fields = (('user', 'card_id'),)
    readonly_fields = ('user', 'card_id')
    list_display = ('card_id', 'lhs_id', username_and_profile)
    search_fields = ('card_id', 'user__id', 'user__name', 'user__nickname')

    def lhs_id(self, object):
        return "%s (%s)" % (object.user.lhsid(), object.user.get_subscribed_display())

class PermissionAdmin(admin.ModelAdmin):
    fields = (('tool', 'user', 'permission'),)
    list_display = ('tool', username_and_profile,
                    'permission', 'addedby', 'date')
    search_fields = ('user__id', 'user__name', 'user__nickname')
    list_filter = ('tool', 'permission')
    autocomplete_fields = ['tool', 'user']

    def save_model(self, request, obj, form, change):
        # are we running with an ldap backend?
        user = get_logged_in_user(request)
        obj.addedby = user
        obj.save()

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return super().has_module_permission(request)
        return is_user_a_tool_maintainer(request)

    # permission checks get a little repetitive across change and delete, so here we
    #   break out that common logic
    # returns a tuple, where the first field indicates if it made a decision, and the second
    # indicates the result. This allows fallthrough.
    def _common_permission_check(self, request, obj=None):
        if obj is None:
            return True, is_user_a_tool_maintainer(request)

        # is this user a maintainer on the tool this permission refers to?
        userpermission = obj.tool.permissions.filter(
            user_id=get_logged_in_user(request).id)
        if (userpermission.count() > 0) and (userpermission.get().permission == 2):
            # users cannot edit their own permissions (unless a superuser)
            # this is actually to prevent users locking themselves out
            if obj.user_id == get_logged_in_user(request).id:
                return True, request.user.is_superuser
            return True, True

        # otherwise, defer to the base
        return False, False

    def has_delete_permission(self, request, obj=None):
        definitive, result = self._common_permission_check(request, obj)
        if not definitive:
            return super().has_delete_permission(request, obj)
        return result

    def has_change_permission(self, request, obj=None):
        definitive, result = self._common_permission_check(request, obj)
        if not definitive:
            return super().has_change_permission(request, obj)
        return result

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # allow the user to select only tools they are a maintainer of
        if db_field.name == "tool" and not request.user.is_superuser:
            kwargs["queryset"] = Tool.objects.filter(
                permissions__permission=2, permissions__user_id=get_logged_in_user(request).id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # this is slightly different to the common check, since it does not need the anti-lockout
    # rule
    def has_view_permission(self, request, obj=None):
        if obj is None:
            return is_user_a_tool_maintainer(request)

        # is this user a maintainer on the tool this permission refers to?
        userpermission = obj.tool.permissions.filter(
            user_id=get_logged_in_user(request).id)
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
    list_display = ('tool', lhs_id, username_and_profile, 'date', 'message')
    list_filter = ('tool',)
    readonly_fields = ('tool', 'user', 'date', 'message')
    search_fields = ('user__id', 'user__name', 'user__nickname',)

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return super().has_module_permission(request)
        return is_user_a_tool_maintainer(request)

    def has_view_permission(self, request, obj=None):
        if obj is None:
            return is_user_a_tool_maintainer(request)

        # is this user a maintainer on the tool this permission refers to?
        userpermission = obj.tool.permissions.filter(
            user_id=get_logged_in_user(request).id)
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

class DJACUserAdmin(DJUserAdmin):
    list_display = ('username', 'name', 'lhs_id', 'email', 'is_staff')
    search_fields = ('username', 'email')


# we don't want to use the Django User object in the admin
# substitute it with our own
admin.site.unregister(DJUser)
admin.site.register(DJACUser, DJACUserAdmin)

admin.site.register(Tool, ToolAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Log, LogAdmin)
