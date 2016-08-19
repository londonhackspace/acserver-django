#!/bin/bash

error=0
log=`mktemp`
touch $log
tmp=/var/www/acserver-django/tmp
# we don't want errors every 10 mins!
limiter=acserver-data-migrate-broken

function check_ret ()
{
	te=$?
	if [ $te -ne 0 ] ; then
		error=$te
		if [ ! -e ${tmp}/${limiter} ] ; then
			echo "error running" $0
			cat $log
			rm -f $log
			exit 1
		fi
		return 1
	fi
	return 0
}



rm -f old-acserver.json

./acserver-dump.py `cat mysql_password` > old-acserver.json 2> $log
check_ret

# This only imports the laser cutter.
../manage.py importoldacserver ./old-acserver.json 5 > $log 2>&1
check_ret

rm -f $log

if [ $error -eq 0 ] ; then
	if [ -e ${tmp}/${limiter} ] ; then
		echo "acserver data migration ok now"
		rm -f ${tmp}/${limiter}
	fi
else
	touch ${tmp}/${limiter}
fi

#
# We don't want tool 1.
#
# need to check whats up with tool 999
#
# see the 2nd comment on:
# https://github.com/londonhackspace/acserver-django/issues/6
#

#for id in 2 3 4 5 6 7 8 9 10 11 12 13 14 999 ; do
#./manage.py importoldacserver ~/acserver.json $id
#done        

#
# the old acnode on the 3-in-1 has been offline for a while
# and the babbage acserver is gone
#
#./manage.py importoldacserver ~jasper/babbage.acserver.json 1 
#
