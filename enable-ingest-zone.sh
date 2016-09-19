#!/bin/bash
source /etc/secrets

set -e

# Strip domain name of the username
user=$(echo $1 | cut -f1 -d"@")
# Get the token from the full path to the ingest zone

token=$(basename $2)

# Creates the token directory
mkdir $2

# Call MirthConnect to set CIFS rights on token directory
timeout 5 curl --user $INGEST_USER:$INGEST_PASSWORD_MIRTHACL "http://fhml-srv024.unimaas.nl:6668/?token=${token}&user=${user}"

exit $?
