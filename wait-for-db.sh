#!/bin/bash
container_id=$1
database_type=$2

function _pg() {
  echo "Testing if pgdb is up and running"
  COUNTER=0
  while [ $COUNTER -lt 120 ]; do
    if docker exec "${container_id}" pg_isready
    then
      echo "Database is running"
      break
    fi
    sleep 1
    echo "Waiting for testdb to finish starting up"
    (( COUNTER=COUNTER+1 ))
  done
}

function _crdb() {
  echo "Testing if crdb is up and running"
  COUNTER=0
  while [ $COUNTER -lt 120 ]; do
    if docker exec "${container_id}" cockroach sql --insecure
    then
      echo "Database is running"
      break
    fi
    sleep 1
    echo "Waiting for testdb to finish starting up"
    (( COUNTER=COUNTER+1 ))
  done
}

"_${database_type}"
