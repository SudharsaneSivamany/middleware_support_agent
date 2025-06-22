#!/bin/bash

case $1 in
    web) if [[ ! -f "/middleware_support_agent/server_maintenance/server_scripts/files/web.txt" ]];
         then
            touch /middleware_support_agent/server_maintenance/server_scripts/files/web.txt
            echo "Web server started successfully `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/web.txt | awk -F' ' '{print $6$7$8}'`"
         else
            echo "Web server already running from `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/web.txt | awk -F' ' '{print $6$7$8}'`"
         fi
         ;;

    app) if [[ ! -f "/middleware_support_agent/server_maintenance/server_scripts/files/app.txt" ]];
         then
            touch /middleware_support_agent/server_maintenance/server_scripts/files/app.txt
            echo "App server started successfully `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/app.txt | awk -F' ' '{print $6$7$8}'`"
         else
            echo "App server already running from `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/app.txt | awk -F' ' '{print $6$7$8}'`"
         fi
         ;;
    db) if [[ ! -f "/middleware_support_agent/server_maintenance/server_scripts/files/db.txt" ]];
         then
            touch /middleware_support_agent/server_maintenance/server_scripts/files/db.txt
            echo "DB server started successfully `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/db.txt | awk -F' ' '{print $6$7$8}'`"
         else
            echo "DB server already running from `ls -ltr /middleware_support_agent/server_maintenance/server_scripts/files/db.txt | awk -F' ' '{print $6$7$8}'`"
         fi
         ;;
esac
