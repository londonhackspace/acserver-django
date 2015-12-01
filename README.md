
Dependencies:

Assuming Debian jessie:

apt-get install python-django python-django-auth-ldap python-sqlite python-psycopg2 python-netaddr python-pip

If you are not on jessie, try pip install ./requirements.txt

For LDAP syncing:

pip install --verbose --no-deps django-ldap-sync

To setup the db run:

./manage.py syncdb

If you are not using LDAP then follow the prompts to create a user for the admin.

If you are usinbg LDAP run:

./manage.py syncldap

also add that to cron every 10 mins or so.

now import the carddb.json:

./manage.py updatecarddb /path/to/carddb.json

(If you just want some initial data to test with you can use server/0_carddb.json)

Using the permissions thing with LDAP:

Go to the "Authentication and Authorization" section of the Django admin and then to Groups.

Add an ACServer Admins group that has all the 'tool' and 'permissions' permissions and
'tool use time | Can add tool use time' and 'log | Can add log'.

Now you can add a user to that group (you have to do it from the users page) and they will be able
to add tools and permissions. Note that they can set a permission for anyone on any tool!

Running tests:

Running all the tests:

./manage.py test

n.b. there are a few sleeps in there, so don;t worry if it pauses for a couple of seconds.

Running just some tests:

./manage.py test server.tests.<testclass>

e.g.

./manage.py test server.tests.ToolTests

you can also run a specific test:

./manage.py test server.tests.ToolTests.test_adduser

Running coverage tests:

You'll need to install the python-coverage package (on debian), on other distros the command may just be 'coverage'

python-coverage run --source='.' manage.py test ; python-coverage html

Todo:

* virtualenv
* permissions for users in the admin:
 * some can make others maintaainers for any tool
 * some users can only maintain some tools
 * most can do nothing
* a nice page of toolusage stats

future things:
	If we get emails in the carddb then send someone an email if they are made a user or maintainer
