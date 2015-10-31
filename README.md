
Dependencies:

apt-get install python-django python-django-auth-ldap python-sqlite python-psycopg2 python-netaddr

To setup the db run:

./manage.py syncdb

Then follow the prompts to create a user for the admin:

now import the carddb.json:

./manage.py updatecarddb /path/to/carddb.json

Todo:

nice admin interface for promoting and demoting users
a nice page of toolusage stats

ldap auth for the admin
permissions for users in the admin:
	some can make others maintaainers for any tool
	some users can only maintain some tools
	most can do nothing

future things:
	If we get emails in the carddb then send someone an email if they are made a user or maintainer
