#!/bin/bash
# utopia       Startup script for the utopia Server
#
# chkconfig: - 85 12
# description: Open source detecting system
# processname: utpia
# Date: 2015-12-16
# Version: 1.0.0
# Site: http://www.utpia.deppon.com
# Author: utopia group

. /etc/init.d/functions
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/deppon/bin

base_dir=$(dirname $0)

PROC_NAME="utopia"
lockfile=/var/lock/subsys/${PROC_NAME}


start() {
	utopia_start=$"Starting ${PROC_NAME} service:"

	if [ -f $lockfile ];then
		 echo "utopia  is running..."
		 success "$utopia_start"
	else
		 daemon python $base_dir/manage.py runserver 0.0.0.0:8000 &>> /tmp/utopia.log 2>&1 &
		 daemon python $base_dir/log_handler.py &> /dev/null 2>&1 &
         sleep 1

		 echo "$utopia_start"
		 nums=0
         for i in manage.py log_handler.py;do
             ps aux | grep "$i" | grep -v 'grep' && let nums+=1 &> /dev/null
         done

         if [ "x$nums" = "x3" ];then
            success "utopia_start"
            touch "$lockfile"
            echo
         else
            failure "$utopia_start"
            echo
         fi

	 fi


}


stop() {

	echo -n $"Stopping ${PROC_NAME} service:"

	if [ -e $lockfile ];then
		ps aux | grep -E 'manage.py|log_handler.py' | grep -v grep | awk '{print $2}' | xargs kill -9 &> /dev/null
		ret=$?

		if [ $ret -eq 0 ]; then
			echo_success
			echo
            rm -f "$lockfile"
		else
			echo_failure
			echo
		fi
	else
			echo_success
			echo

	fi
}

restart(){
    stop
    start
}

# See how we were called.
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;

  restart)
        restart
        ;;

  *)
        echo $"Usage: $0 {start|stop|restart}"
        exit 2
esac