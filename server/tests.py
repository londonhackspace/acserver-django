import datetime, time, json

from django.test import TestCase
from django.test import Client
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

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

    self.user_does_not_exist = 0x12345678
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

#
# things to add (missing in coverage tests)
#
# permissions save with and without date
# user.lhsid
# user.username_and_profile
# grant_to_card for a tool that does not exist
# grant_to_card for a permission that already exists.
# settoolstatus for a tool that does not exist
# settoolstatus - put a tool in service?
#

#
# importoldacserver
# updatecarddb
#

