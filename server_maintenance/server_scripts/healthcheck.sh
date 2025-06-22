#!/bin/bash

case $1 in
    web) if [[ ! -f "/middleware_support_agent/server_maintenance/server_scripts/files/web.txt" ]];
         then
            echo "Web server not running"
         else
            echo "Web server started and running from  `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/web.txt | awk -F' ' '{print $6$7$8}'`"
         fi
         ;;

    app) if [[ ! -f "/middleware_support_agent/server_maintenance/server_scripts/files/app.txt" ]];
         then
            echo "App server not running"
         else
            echo "App server started and running from  `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/app.txt | awk -F' ' '{print $6$7$8}'`"
         fi
         ;;
    db) if [[ ! -f "/middleware_support_agent/server_maintenance/server_scripts/files/db.txt" ]];
         then
            echo "DB server not running"
         else
            echo "DB server started and running from  `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/db.txt | awk -F' ' '{print $6$7$8}'`"
         fi
         ;;
esac
