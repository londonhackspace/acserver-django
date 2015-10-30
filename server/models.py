from django.db import models
from django.utils.html import format_html
from django.utils import timezone

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
    return u"%s : '%s' (%s)" % (self.lhsid(), self.name, self.get_subscribed_display(),)

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

# tool
class Tool(models.Model):
  name = models.TextField()
  status = models.PositiveIntegerField(default=0, choices = ((1, "Operational"), (0, "Out of service")))
  status_message = models.TextField()
  inuse = models.BooleanField(default=False, choices = ((True, "yes"),(False, "no")))
  inuseby = models.ForeignKey(User, null=True, default=None)
  # can be null cos some acnodes may be running old code.
  secret = models.CharField(max_length=8, null=True)

  def __unicode__(self):
    return u"%s (id: %d)" % (self.name, self.id)

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

class Permissions(models.Model):
  user = models.ForeignKey(User)
  tool = models.ForeignKey(Tool)
  permission = models.PositiveIntegerField(choices = ((1, "user"),(2, "maintainer")))
  addedby = models.ForeignKey(User, related_name="addedpermissions")
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
    return super(Permissions, self).save(*args, **kwargs)

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
