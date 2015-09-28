from django.db import models

# Create your models here.


# user
class User(models.Model):
  # the id field is created automatticly by django
  # we use the id's from the carddb tho
  # might want to disable auto_increment?
  name = models.CharField(max_length=50)
  subscribed = models.BooleanField(default=False)
  
  def __unicode__(self):
    return u"%d %s: %s" % (self.id, self.name, str(self.subscribed))

# tool
class Tool(models.Model):
  name = models.TextField()
  status = models.PositiveIntegerField(default=0, choices = ((1, "Operational"), (0, "Out of service")))
  status_message = models.TextField()
  inuse = models.BooleanField(default=False, choices = ((True, "yes"),(False, "no")))
  inuseby = models.ForeignKey(User, null=True, default=None)
  # shared secret

  def __unicode__(self):
    return u"%d %s: %d - %s" % (self.id, self.name, self.status, self.status_message)

class ToolUseTime(models.Model):
  tool = models.ForeignKey(Tool)
  inuseby = models.ForeignKey(User)
  duration = models.PositiveIntegerField()

# card
class Card(models.Model):
  # foreigen key to user.id
  user = models.ForeignKey(User)
  # actually only need 14, the uid is stored as hex.
  card_id = models.CharField(max_length=15, db_index=True)

  def __unicode__(self):
    return u"%d %s" % (self.id, self.card_id)

class Permissions(models.Model):
  user = models.ForeignKey(User)
  tool = models.ForeignKey(Tool)
  permission = models.PositiveIntegerField(choices = ((1, "user"),(2, "maintainer")))

  def __unicode__(self):
    return u"%s is a %s for %s" % (self.user.name, self.get_permission_display(), self.tool.name)

