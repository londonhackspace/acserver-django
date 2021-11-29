# London Hackspace ACNode Server

## Docker Development Environment

Copy `acserver/ldap_local_settings_example.py` to `local_settings.py` remove the DB configuration and run `docker-compose up` for a functional development environment

To create an initial user for testing:

```
docker-compose exec server python manage.py createsuperuser
```

## venv Development Environment

Assuming Debian/Ubuntu:

```
apt-get install python-django python-django-auth-ldap python-sqlite python-psycopg2 python-netaddr python-pip
```

Also and/or otherwise try running `make`, the included Makefile should build a virtualenv with the right bits in it for you. You can activate the virtualenv with `. ./venv/bin/activate`

## For LDAP syncing:

If you are usinbg LDAP run:

```
./manage.py syncldap
```

also add that to cron every 10 mins or so.

now import the carddb.json:

```
./manage.py updatecarddb /path/to/carddb.json
```

(If you just want some initial data to test with you can use `server/test_data/0_carddb.json`)

## Using the permissions thing with LDAP:

Go to the "Authentication and Authorization" section of the Django admin and then to Groups.

Add an ACServer Admins group that has all the 'tool' and 'permissions' permissions and
'tool use time | Can add tool use time' and 'log | Can add log'.

Now you can add a user to that group (you have to do it from the users page) and they will be able
to add tools and permissions. Note that they can set a permission for anyone on any tool!

## Running tests:

Running all the tests:

```
./manage.py test
```

n.b. there are a few sleeps in there, so don't worry if it pauses for a couple of seconds.

### Running just some tests:

```
./manage.py test server.tests.<testclass>
```

e.g.

```
./manage.py test server.tests.ToolTests
```

you can also run a specific test:

```
./manage.py test server.tests.ToolTests.test_adduser
```

### Running coverage tests:

You'll need to install the python-coverage package (on debian), on other distros the command may just be 'coverage'

```
python-coverage run --source='.' manage.py test ; python-coverage html
```

Todo:

- permissions for users in the admin:
- some can make others maintainers for any tool
- some users can only maintain some tools
- most can do nothing
- a nice page of tool usage stats

future things:
If we get emails in the carddb then send someone an email if they are made a user or maintainer
