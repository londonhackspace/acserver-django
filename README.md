
Dependencies:

apt-get install python-django python-django-auth-ldap python-sqlite python-psycopg2 python-netaddr

To setup the db run:

./manage.py syncdb

Then follow the prompts to create a user for the admin:

now import the carddb.json:

./manage.py updatecarddb /path/to/carddb.json

Todo:

* login page for non-admin users that lets them see there tool permissions (same as the main website via the api)
 * above also means the user object will be populated from LDAP
* permissions for users in the admin:
 * some can make others maintaainers for any tool
 * some users can only maintain some tools
 * most can do nothing
* a nice page of toolusage stats

future things:
	If we get emails in the carddb then send someone an email if they are made a user or maintainer
