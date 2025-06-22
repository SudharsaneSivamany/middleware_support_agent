#!/bin/bash

case $1 in
    web) if [[ -f "/middleware_support_agent/server_maintenance/server_scripts/files/web.txt" ]];
         then
            rm /middleware_support_agent/server_maintenance/server_scripts/files/web.txt
            echo "Web server stopped successfully"
         else
            echo "Web server is not running already"
         fi
         ;;

    app) if [[ -f "/middleware_support_agent/server_maintenance/server_scripts/files/app.txt" ]];
         then
            rm /middleware_support_agent/server_maintenance/server_scripts/files/app.txt
            echo "App server stopped successfully"
         else
            echo "App server is not running already"
         fi
         ;;
    db) if [[ -f "/middleware_support_agent/server_maintenance/server_scripts/files/db.txt" ]];
         then
            rm /middleware_support_agent/server_maintenance/server_scripts/files/db.txt
            echo "DB server stopped successfully"
         else
            echo "DB server is not running already"
         fi
         ;;
esac
