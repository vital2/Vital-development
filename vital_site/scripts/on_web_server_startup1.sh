#!/bin/bash

dbhost=$(awk -F ":" '/VITAL_DB_HOST/ {print $2}' /home/vital/config.ini | tr -d ' ')
dbpass=$(awk -F ":" '/VITAL_DB_PWD/ {print $2}' /home/vital/config.ini | tr -d ' ')
dbname=$(awk -F ":" '/VITAL_DB_NAME/ {print $2}' /home/vital/config.ini | tr -d ' ')
dbuser=$(awk -F ":" '/VITAL_DB_USER/ {print $2}' /home/vital/config.ini | tr -d ' ')
dbport=$(awk -F ":" '/VITAL_DB_PORT/ {print $2}' /home/vital/config.ini | tr -d ' ')
#sftp=$(awk -F ":" '/SFTP_ADDR/ {print $2}' /home/vital/config.ini | tr -d ' ')
#localrepo=$(awk -F ":" '/LOCAL_REPO/ {print $2}' /home/vital/config.ini | tr -d ' ')

# sets up required bridges and bonds for the courses on web server
nets=$(PGPASSWORD=$dbpass psql -U $dbuser -d $dbname -h $dbhost -p $dbport -t -c "SELECT c.id from vital_course c join vital_network_configuration n on c.id=n.course_id where c.status='ACTIVE' and n.is_course_net=True")
set -f
#echo "sahil"
#echo $nets
array=(${nets// / })

for var in "${array[@]}"
do
    echo $var 
    /home/vital/vital2.0/source/virtual_lab/vital_site/scripts/ws_course_network_startup1.sh $var
done
