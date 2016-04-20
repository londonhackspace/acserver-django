apt-get update
apt-get install -y python-django python-django-auth-ldap python-sqlite python-psycopg2 python-netaddr python-pip

cd /vagrant
./manage.py syncdb --noinput
./manage.py updatecarddb carddb.json

nohup ./manage.py runserver 0.0.0.0:1234 &

