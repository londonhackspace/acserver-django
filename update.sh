#!/bin/bash

error=0
log=`mktemp`
touch $log
tmp=/var/www/acserver/tmp

function check_ret ()
{
	te=$?
	if [ $te -ne 0 ] ; then
		error=$te
		if [ ! -e ${tmp}/acserver-update-broken ] ; then
			cat $log
		fi
		return 1
	fi
	return 0
}

cd /var/www/acserver
. ./venv/bin/activate

wget https://london.hackspace.org.uk/carddb.php -O ${tmp}/carddb.json > $log 2>&1
check_ret

/var/www/acserver/manage.py updatecarddb ${tmp}/carddb.json > $log 2>&1
check_ret

rm -f ${tmp}/carddb.json
/var/www/acserver/manage.py syncldap > $log 2>&1
check_ret

rm -f $log

if [ $error -eq 0 ] ; then
	if [ -e ${tmp}/acserver-update-broken ] ; then
		echo "acserver update ok now"
		rm -f ${tmp}/acserver-update-broken
	fi
else
	touch ${tmp}/acserver-update-broken
fi
