from django.db import models
from django.utils.html import format_html
from django.utils import timezone
# yes, the acserver user object is called User, same as the django one, so we call it
# DJUser...
from django.contrib.auth.models import User as DJUser

import sys, datetime, logging

# user
class User(models.Model):
  # the id field is created automatticly by django
  # we use the id's from the carddb tho
  # might want to disable auto_increment?
  # I'd like the name to be unique=True, but the carddb export does:
  #
  # ifnull(u.nickname, u.full_name) nick,
  #
  # which can lead to duplicate names...
  name = models.TextField()
  subscribed = models.BooleanField(default=False, choices = ((True, "Subscribed"), (False, "Not Subscribed")))
  
  def __unicode__(self):
    o = u"%s : '%s' (%s)" % (self.lhsid(), self.name, self.get_subscribed_display(),)
    if hasattr(sys.stdout, "encoding"):
      if not sys.stdout.encoding:
        return unicode(o).encode("ascii", "replace")
    return o

  def __str__(self):
    return self.__unicode__()

  def lhsid(self):
    if self.id == None:
      return u"HSXXXXX"
    return u"HS%05d" % (self.id)
  lhsid.admin_order_field = 'id'

  def username_and_profile(u):
    return u'<a href="https://london.hackspace.org.uk/members/profile.php?id=%d">%s</a>' % (u.id, format_html(u.name))
  username_and_profile.short_description = 'Name'
  username_and_profile.allow_tags = True
  username_and_profile.admin_order_field = 'name'

  class Meta:
    unique_together = (("id", "name"),)
    verbose_name = 'ACNode User'
    ordering = ['id']

# tool
class Tool(models.Model):
  name = models.TextField()
  status = models.PositiveIntegerField(default=0, choices = ((1, "Operational"), (0, "Out of service")))
  # If a tool is in service the status_message should be 'OK'
  # cos the website depends on that :/
  status_message = models.TextField()
  inuse = models.BooleanField(default=False, choices = ((True, "yes"),(False, "no")))
  inuseby = models.ForeignKey(User, null=True, default=None)
  # can be null cos some acnodes may be running old code.
  secret = models.CharField(max_length=8, blank=True, default="")
  secret.help_text = "The shared secret to use with the acnode, only for version 0.8 or better acnodes"

  def __unicode__(self):
    return u"%s (id: %d)" % (self.name, self.id)

  def __str__(self):
    return self.__unicode__()


class ToolUseTime(models.Model):
  tool = models.ForeignKey(Tool)
  inuseby = models.ForeignKey(User)
  duration = models.PositiveIntegerField()

  def __unicode__(self):
    return u"%s used by %s for %s" % (self.tool, self.inuseby, str(datetime.timedelta(seconds=self.duration)))

# card
class Card(models.Model):
  # foreigen key to user.id
  user = models.ForeignKey(User)
  # actually only need 14, the uid is stored as hex.
  card_id = models.CharField(max_length=15, db_index=True, unique=True)

  def __unicode__(self):
    return u"%d %s" % (self.id, self.card_id)

class Permission(models.Model):
  user = models.ForeignKey(User)
  tool = models.ForeignKey(Tool)
  permission = models.PositiveIntegerField(choices = ((1, "user"),(2, "maintainer")))
  addedby = models.ForeignKey(User, related_name="addedpermission")
  date = models.DateTimeField()

  def __unicode__(self):
    return u"%s is a %s for %s, added by <%s> on %s" % (self.user.name, self.get_permission_display(), self.tool.name, self.addedby, self.date)

  def save(self, *args, **kwargs):
    # if we don't have a date field, set it to the
    # current date and time.
    if not self.date:
      self.date = timezone.now()
    if self.id:
      # object already exists, so update the datestamp on change...
      self.date = timezone.now()
    return super(Permission, self).save(*args, **kwargs)

  class Meta:
    unique_together = (("user", "tool"),)

class Log(models.Model):
  tool = models.ForeignKey(Tool)
  user = models.ForeignKey(User)
  date = models.DateTimeField()
  message = models.TextField()
  time = models.PositiveIntegerField(default=0)

  def __unicode__(self):
    return u"at %s %s on %s : message: %s" % (self.date, self.user.name, self.tool.name, self.message)

  def save(self, *args, **kwargs):
    # if we don't have a date field, set it to the
    # current date and time.
    if not self.date:
      self.date = timezone.now()
    return super(Log, self).save(*args, **kwargs)

#
# A proxy for the django User object
# that makes all maintainers a staff member so they can log into the admin
# UI
#
# This dosn't give them any permissions to do anything tho!
#
class DJACUser(DJUser):
  class Meta:
    proxy = True
#    app_label = 'auth'
    verbose_name = 'User'

  def __getattribute__(self, name):
    logger = logging.getLogger('django')
    parent = super(DJACUser, self).__getattribute__(name)
    if name == 'is_staff':
      try:
        acu = User.objects.get(pk=self.id)
      except Exception as e:
        # XXX ObjectDoesNotExist if it's not an acnode user.
        # should never happen on the live server(?)
        logger.critical('exception in DJACUser __getattribute__ for %s : %s', str(name), e)
        return parent
      if len(acu.permission_set.filter(permission=2).all()) > 0:
        return True
    return object.__getattribute__(self, name)
