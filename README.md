
Dependencies:

apt-get install python-django python-django-auth-ldap python-sqlite python-psycopg2 python-netaddr python-pip

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

Using the permissions thing with LDAP:

Go to the "Authentication and Authorization" section of the Django admin and then to Groups.

Add an ACServer Admins group that has all the 'tool' and 'permissions' permissions and
'tool use time | Can add tool use time' and 'log | Can add log'.

Now you can add a user to that group (you have to do it from the users page) and they will be able
to add tools and permissions. Note that they can set a permission for anyone on any tool!

Todo:

* permissions for users in the admin:
 * some can make others maintaainers for any tool
 * some users can only maintain some tools
 * most can do nothing
* a nice page of toolusage stats

future things:
	If we get emails in the carddb then send someone an email if they are made a user or maintainer
