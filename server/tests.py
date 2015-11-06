import datetime, time, json, os

from django.test import TestCase
from django.test import Client
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core import management

from server.models import Tool, Card, User, Permission

class ToolTests(TestCase):
  def setUp(self):
    t = Tool(id=1, name='test_tool', status=1, status_message='working ok')
    t.save()

    t = Tool(id=2, name='other test tool', status=0, status_message='Out of action')
    t.save()

    users = (
      # user 1 has 2 cards, and is a maintainer
      (1, 'user1a', '00112233445566', True),
      (1, 'user1b', 'aabbccdd', True),

      # a user
      (2, 'user2', '22222222', True),

      # subscribed, but not a user
      (3, 'user3', '33333333', True),

      # exists, but not is not subscribed
      (4, 'user4', '44444444', False),
    )

    for id, name, card, subscribed in users:
      self.__dict__[name] = card
      try:
        u = User.objects.get(pk=id)
        u.card_set.add(Card(card_id=card))
        u.save()
      except ObjectDoesNotExist:
        u = User(id=id, name=name, subscribed=subscribed)
        u.card_set.add(Card(card_id=card))
        u.save()

    self.user_does_not_exist = '12345678'
    # user 2 is a user
    p = Permission(user=User.objects.get(pk=2), permission=1, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
    p.save()
    # user 1 is a maintainer
    p = Permission(user=User.objects.get(pk=1), permission=2, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
    p.save()
    # make the android tag a user
#    p = Permissions(user=User.objects.get(pk=8), permission=1, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
#    p.save()
    # make the temp card a maintainer
#    p = Permissions(user=User.objects.get(pk=5), permission=2, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
#    p.save()
    # make user 4 a maintainer
    p = Permission(user=User.objects.get(pk=4), permission=2, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
    p.save()

  def test_online(self):
    # should be online now
    client = Client()
    resp = client.get('/%d/status/' % 1)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_online_tool_does_not_exist(self):
    # test with an unknown tool_id
    client = Client()
    resp = client.get('/%d/status/' % 123)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_card_not_exists(self):
    client = Client()
    resp = client.get('/1/card/%s' % self.user_does_not_exist)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_user(self):
    client = Client()
    resp = client.get('/1/card/%s' % self.user2)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_user_exists_and_not_user(self):
    client = Client()
    resp = client.get('/1/card/%s' % self.user3)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_user_and_not_subscribed(self):
    client = Client()
    resp = client.get('/1/card/%s' % self.user4)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_maintainer(self):
    client = Client()
    resp = client.get('/1/card/%s' % self.user1a)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '2')

  def test_maintainer_multi_cards(self):
    client = Client()
    resp = client.get('/1/card/%s' % self.user1b)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '2')

  def test_adduser(self):
    client = Client()

    # now the maintainer gives user id 3 permission to use the tool
    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user3, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # and now they can use the tool
    resp = client.get('/1/card/%s' % self.user3)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_add_unknown(self):
    # maintainer add unknown card
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user_does_not_exist, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_add_tool_does_not_exist(self):
    # add a card to a tool that does not exist
    client = Client()

    resp = client.post('/42/grant-to-card/%s/by-card/%s' % (self.user3, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_add_permission_exists(self):
    # add a user to a tool that that user is already a user on.
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user2, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_add_unsubscribed(self):
    # maintainer adds known, unsubscribed card
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user4, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_non_maintainer_add(self):
    # know user tries to add a card
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user3, self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_unknown_user_adds_a_card(self):
    # unknown user tries to add a card
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user3, self.user_does_not_exist))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_noperms_user_adds_a_card(self):
    # known user with no perms for this tool tries to add a card
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user3, self.user3))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_unsubscribed_maintainer_adds_a_card(self):
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user3, self.user4))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_user_already_has_perms(self):
    client = Client()

    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user2, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_using_acnode(self):
    client = Client()

    resp = client.post('/1/tooluse/1/%s' % (self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # and stop after 5 seconds
    time.sleep(5)
    resp = client.post('/1/tooluse/time/for/%s/%d' % (self.user2, 5))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    resp = client.post('/1/tooluse/0/%s' % (self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_toolusetime_tool_does_not_exist(self):
    client = Client()

    resp = client.post('/42/tooluse/time/for/%s/%d' % (self.user2, 5))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_toolusetime_user_does_not_exist(self):
    client = Client()

    resp = client.post('/1/tooluse/time/for/%s/%d' % (self.user_does_not_exist, 5))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_tooluse_user_does_not_exist(self):
    client = Client()

    # card does not exist
    resp = client.post('/1/tooluse/1/%s' % (self.user_does_not_exist))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_tooluse_tool_does_not_exist(self):
    client = Client()
    # tool does not exist
    resp = client.post('/42/tooluse/1/%s' % (self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_set_offline(self):
    # take the tool offline
    client = Client()
    resp = client.post('/1/status/0/by/%s' % (self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_unknown_set_offline(self):
    # only known users can take a tool offline
    client = Client()
    resp = client.post('/1/status/0/by/%s' % (self.user_does_not_exist))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_not_user_set_offline(self):
    # known but not a user
    client = Client()
    resp = client.post('/1/status/0/by/%s' % (self.user3))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_set_offline_tool_does_not_exists(self):
    # set an unknown tool offline
    client = Client()
    resp = client.post('/42/status/0/by/%s' % (self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_set_offline_and_online(self):
    # set a tool offline and then back online
    client = Client()

    resp = client.post('/1/status/0/by/%s' % (self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    resp = client.post('/1/status/1/by/%s' % (self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

  def test_new_user_put_offline(self):
    client = Client()

    # let them use the tool
    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user3, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # check that they can use it
    resp = client.get('/1/card/%s' % self.user3)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # and take the tool out of service
    resp = client.post('/1/status/0/by/%s' % (self.user3))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # and we should be out of service now
    resp = client.get('/%d/status/' % 1)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_non_maintainer_set_online(self):
    client = Client()

    # take the tool offline
    resp = client.post('/1/status/0/by/%s' % (self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # non maintainer putting online
    resp = client.post('/1/status/1/by/%s' % (self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '0')

  def test_error(self):
    # this test fails atm, it's not a big deal tho.
    client = Client()
    resp = client.get('/42/card/%s' % '00000000')
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '-1')

  def test_toolisinuse(self):
    # not called by the acnodes, but by things monitoring them.
    client = Client()

    # start using the tool
    resp = client.post('/1/tooluse/1/%s' % (self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    resp = client.get('/%d/is_tool_in_use' % (1,))
    self.assertEqual(resp.status_code, 200)
    self.failUnless(resp.content == "yes")

    # if the tool starts and stops in the same second then this fails
    time.sleep(1)

    # and stop
    resp = client.post('/1/tooluse/0/%s' % (self.user2))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    resp = client.get('/%d/is_tool_in_use' % (1,))
    self.assertEqual(resp.status_code, 200)
    # this fails if the tool is used for less than a second actual bug?
    self.failUnless(resp.content == "no")

  def test_nonexistant_tool_in_use(self):
    client = Client()
    resp = client.get('/%d/is_tool_in_use' % (42,))
    self.assertEqual(resp.status_code, 200)

    # tool does not exist
    self.failUnless(resp.content == "-1")

  # apikey tests
  # API-KEY: 'KEY GOES HERE'
  def test_get_tools_summary_for_user(self):
    # get_tools_summary_for_user
    client = Client()

    # "/api/get_tools_summary_for_user/%d" % (2)
    resp = client.get('/api/get_tools_summary_for_user/%d' % (1,), HTTP_API_KEY='KEY GOES HERE')
    self.assertEqual(resp.status_code, 200)
    ret = json.loads(resp.content)
    self.failUnless(ret[0]['permission'] == 'maintainer')

  def test_get_tools_summary_for_user_toolstuff(self):
    # get_tools_summary_for_user
    client = Client()
    # "/api/get_tools_summary_for_user/%d" % (2)
    resp = client.get('/api/get_tools_summary_for_user/%d' % (1,), HTTP_API_KEY='KEY GOES HERE')
    self.assertEqual(resp.status_code, 200)
    ret = json.loads(resp.content)
    self.failUnless(ret[0]['permission'] == 'maintainer')
    self.failUnless(ret[0]['status'] == 'Operational')
    self.failUnless(ret[0]['status_message'] == 'working ok')
    self.failUnless(ret[0]['name'] == 'test_tool')
    self.failUnless(ret[0]['in_use'] == 'no')

  def test_get_tools_summary_for_user_does_not_exist(self):
    # get_tools_summary_for_user for user who does not exist
    client = Client()
    # "/api/get_tools_summary_for_user/%d" % (2)
    resp = client.get('/api/get_tools_summary_for_user/%d' % (42,), HTTP_API_KEY='KEY GOES HERE')
    self.assertEqual(resp.status_code, 200)
    ret = json.loads(resp.content)
    self.failUnless(ret[0]['permission'] == 'un-authorised')
    self.failUnless(ret[1]['permission'] == 'un-authorised')

  def test_get_tools_summary_for_user_adding_user(self):
    # get_tools_summary_for_user for user who is not authorised, and
    # then add them, then test again
    client = Client()

    resp = client.get('/api/get_tools_summary_for_user/%d' % (3,), HTTP_API_KEY='KEY GOES HERE')
    self.assertEqual(resp.status_code, 200)
    ret = json.loads(resp.content)
    self.failUnless(ret[0]['permission'] == 'un-authorised')

    # add user 3 as a user
    resp = client.post('/1/grant-to-card/%s/by-card/%s' % (self.user3, self.user1a))
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # and now they can use the tool
    resp = client.get('/1/card/%s' % self.user3)
    self.assertEqual(resp.status_code, 200)
    self.assertEqual(resp.content, '1')

    # now check they can use the tool
    resp = client.get('/api/get_tools_summary_for_user/%d' % (3,), HTTP_API_KEY='KEY GOES HERE')
    self.assertEqual(resp.status_code, 200)
    ret = json.loads(resp.content)
    self.failUnless(ret[0]['permission'] == 'user')

  def test_get_tools_summary_for_user_wrong_api_key(self):
    # get_tools_summary_for_user with wrong api key
    client = Client()

    resp = client.get('/api/get_tools_summary_for_user/%d' % (42,), HTTP_API_KEY='udlrabss')
    self.assertEqual(resp.status_code, 401)
    self.failUnless(resp.content.startswith('HTTP Error 401'))

  def test_get_tools_summary_for_user_no_api_key(self):
    # get_tools_summary_for_user with wrong api key
    client = Client()

    resp = client.get('/api/get_tools_summary_for_user/%d' % (42,))
    self.assertEqual(resp.status_code, 401)
    self.failUnless(resp.content.startswith('API Key required'))

class ModelTests(TestCase):
  def setUp(self):
    t = Tool(id=1, name='test_tool', status=1, status_message='working ok')
    t.save()

    u = User(id=1, name='Test user', subscribed=True)
    u.card_set.add(Card(card_id='12345678'))
    u.save()

  def test_permission_nodate(self):
    # if we save a permission with no date it should get the current date added.
    p = Permission(user=User.objects.get(pk=1), tool=Tool.objects.get(pk=1), permission=1, addedby=User.objects.get(pk=1))
    p.save()
    self.failUnless(p.date != None)

  def test_permission_date(self):
    # permissions can have dates in the past, e.g. if we are importing old logs
    now = timezone.now() - datetime.timedelta(days=30)
    p = Permission(user=User.objects.get(pk=1), tool=Tool.objects.get(pk=1), permission=1, addedby=User.objects.get(pk=1), date=now)
    p.save()
    self.failUnless(p.date == now)

  def test_permission_updated(self):
    # if a permission is changed the date should be updated.
    p = Permission(user=User.objects.get(pk=1), tool=Tool.objects.get(pk=1), permission=1, addedby=User.objects.get(pk=1))
    p.save()
    self.failUnless(p.date != None)
    p2 = Permission.objects.get(user=User.objects.get(pk=1), tool=Tool.objects.get(pk=1))
    # upgrde to maintainer
    p2.permission = 2
    p2.save()
    self.failUnless(p.date < p2.date)

  def test_user_lhsid(self):
    u = User.objects.get(pk=1)
    self.failUnless(u.lhsid() == 'HS00001')

  def test_user_lhsid2(self):
    u = User(id=42, name='t2', subscribed=True)
    self.failUnless(u.lhsid() == 'HS00042')

  def test_user_username_and_profile(self):
    u = User(id=42, name='t2', subscribed=True)
    self.failUnless(u.username_and_profile() == '<a href="https://london.hackspace.org.uk/members/profile.php?id=42">t2</a>')

class SecretTests(TestCase):
  user3  = '33333333'
  user3a = '33333300'
  user4  = '44444444'

  def setUp(self):
    self.update_carddb('0_carddb.json')
    t = Tool(id=1, name='test_tool', status=1, status_message='working ok')
    t.save()
    t = Tool(id=2, name='test_tool_with_secret', status=1, status_message='working ok', secret='12345678')
    t.save()
    # make user 3 a user for tool 1
    p = Permission(user=User.objects.get(pk=3), permission=1, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
    p.save()
    # and 2
    p = Permission(user=User.objects.get(pk=3), permission=1, tool=Tool.objects.get(pk=2), addedby=User.objects.get(pk=1))
    p.save()

  def update_carddb(self, file):
    management.call_command('updatecarddb', os.getcwd() + os.path.sep + 'server' + os.path.sep + file, verbosity=2)

  def querycard(self, card, code=200, secret=None, tool=1):
    client = Client()

    if not secret:
      resp = client.get('/%d/card/%s' % (tool, card,))
    else:
      resp = client.get('/%d/card/%s' % (tool, card,), HTTP_X_AC_KEY = secret)
    self.assertEqual(resp.status_code, code)
    return(resp.content)

  def query_secret(self, card):
    return self.querycard(card, secret='12345678', tool=2)

  def test_start(self):
    # card exists and is a user for this tool
    self.failUnless(self.querycard(self.user3) == '1')
    # this card does not exist yet
    self.failUnless(self.querycard(self.user3a) == '-1')

    # card exists and is a user for this tool
    self.failUnless(self.query_secret(self.user3) == '1')
    # this card does not exist yet
    self.failUnless(self.query_secret(self.user3a) == '-1')

  def test_node_missing_secret(self):
    # card exists and is a user for this tool
    # but the secret is missing now so it will fail
    self.failUnless(self.querycard(self.user3, tool=2) == '0')

  def test_Server_missing_secret(self):
    # we are sending an unexpected secret. the server should accept it (and log it)
    self.failUnless(self.querycard(self.user3, secret='abcdefgh') == '1')

  def test_wrong_secret(self):
    # we are sending the wrong secret, so should be refused
    self.failUnless(self.querycard(self.user3, tool=2, secret='abcdefgh') == '0')

class CheckIpTests(TestCase):
  def setUp(self):
    t = Tool(id=1, name='test_tool', status=1, status_message='working ok')
    t.save()

    u = User(id=1, name='Test user', subscribed=True)
    u.card_set.add(Card(card_id='12345678'))
    u.save()

    # make user 1 a user for tool 1
    p = Permission(user=User.objects.get(pk=1), permission=1, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
    p.save()

  def test_check_ip(self):
    with self.settings(ACNODE_IP_RANGE='1.2.3.0/24'):
      client = Client()
      resp = client.get('/1/card/%s' % ('12345678',))
      self.assertEqual(resp.status_code, 403)
      self.assertEqual(resp.content, "IP forbidden\n")

# updatecarddb tests
class DbUpdateTests(TestCase):

  def setUp(self):
    self.update_carddb('0_carddb.json')
    t = Tool(id=1, name='test_tool', status=1, status_message='working ok')
    t.save()
    # make user3 a user
    p = Permission(user=User.objects.get(pk=3), permission=1, tool=Tool.objects.get(pk=1), addedby=User.objects.get(pk=1))
    p.save()
    self.user3 = '33333333'
    self.user3a = '33333300'

  def querycard(self, card, code=200):
    client = Client()

    resp = client.get('/1/card/%s' % (card,))
    self.assertEqual(resp.status_code, code)
    return(resp.content)

  def update_carddb(self, file):
    management.call_command('updatecarddb', os.getcwd() + os.path.sep + 'server' + os.path.sep + file, verbosity=2)

  def test_start(self):
    client = Client()

    ret = self.querycard(self.user3)
    self.assertEqual(ret, '1')

    ret = self.querycard(self.user3a)
    self.assertEqual(ret, '-1')

  def test_cardb_updates(self):
    # this card does not exist yet
    self.failUnless(self.querycard(self.user3a) == '-1')
    self.update_carddb("1_card_added_carddb.json")

    # should exist now
    self.failUnless(self.querycard(self.user3a) == '1')
    self.update_carddb("2_card_removed_carddb.json")

    # and now it's gone
    self.failUnless(self.querycard(self.user3a) == '-1')

    # user3 should be ok
    self.failUnless(self.querycard(self.user3) == '1')

    # un subscribe them
    self.update_carddb("3_user_unsubscribed_carddb.json")
    # and now they don't work
    self.failUnless(self.querycard(self.user3) == '-1')

    # re-subscribe them
    self.update_carddb("4_user_subscribed_carddb.json")
    # and now they should work
    self.failUnless(self.querycard(self.user3) == '1')

# importoldacserver
class ImportOldTests(TestCase):

  def import_old_acserver(self, file, toolid=None):
    if not toolid:
      management.call_command('importoldacserver', os.getcwd() + os.path.sep + 'server' + os.path.sep + file, verbosity=2)
    else:
      management.call_command('importoldacserver', os.getcwd() + os.path.sep + 'server' + os.path.sep + file, str(toolid), verbosity=2)

  def update_carddb(self, file):
    management.call_command('updatecarddb', os.getcwd() + os.path.sep + 'server' + os.path.sep + file, verbosity=2)

  def setUp(self):
    self.update_carddb('0_carddb.json')
    self.user3 = '33333333'
    self.user3a = '33333300'

  def test_import(self):
    self.import_old_acserver('old-acserver-dump_0.json')

    t = Tool.objects.get(pk=1)
    self.failUnless(t.name == 'test_tool')
    self.failUnless(t.status == 1)

    p = Permission.objects.get(user=User.objects.get(pk=3), tool=t)
    self.failUnless(p.permission == 1)

  def test_import_two_tools(self):
    self.import_old_acserver('old-acserver-dump_1.json')

    t = Tool.objects.get(pk=1)
    self.failUnless(t.name == 'test_tool')
    self.failUnless(t.status == 1)

    p = Permission.objects.get(user=User.objects.get(pk=3), tool=t)
    self.failUnless(p.permission == 1)

    t2 = Tool.objects.get(pk=2)
    self.failUnless(t2.name == 'test_tool2')
    self.failUnless(t2.status == 0)

    # they are a maintainer here
    p = Permission.objects.get(user=User.objects.get(pk=3), tool=t2)
    self.failUnless(p.permission == 2)

  def test_import_filter(self):
    self.import_old_acserver('old-acserver-dump_1.json', 1)

    t = Tool.objects.get(pk=1)
    self.failUnless(t.name == 'test_tool')
    self.failUnless(t.status == 1)

    p = Permission.objects.get(user=User.objects.get(pk=3), tool=t)
    self.failUnless(p.permission == 1)

    # we only imported tool 1
    try:
      t2 = Tool.objects.get(pk=2)
      self.failUnless(False == True)
    except ObjectDoesNotExist:
      # this actually throws a DoesNotExist exception - I can't find the defination of it
      # so i can't get one to compare against with assertThrows()...
      # this works tho.
      pass

  def test_import_change_permission(self):
    self.import_old_acserver('old-acserver-dump_0.json')

    t = Tool.objects.get(pk=1)
    self.failUnless(t.name == 'test_tool')
    self.failUnless(t.status == 1)

    p = Permission.objects.get(user=User.objects.get(pk=3), tool=t)
    self.failUnless(p.permission == 1)

    # now import a newer version, in this one user 3 is now a maintainer
    self.import_old_acserver('old-acserver-dump_2.json')

    p = Permission.objects.get(user=User.objects.get(pk=3), tool=t)
    self.failUnless(p.permission == 2)


