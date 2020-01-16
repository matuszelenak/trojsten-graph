#!/usr/bin/env bash
set -e

export POSTGRES_USER="${POSTGRES_USER:-graph}"
export POSTGRES_DB="${POSTGRES_DB:-graph}"

env | grep '^POSTGRES'

if [[ ! -z "$POSTGRES_HOST" && "$POSTGRES_HOST" != "localhost" &&  "$POSTGRES_HOST" != "127.0.0.1" ]]; then
    echo
    read -p "Going to DROP the database on $POSTGRES_HOST. Continue? [y/N]: "

    if [[ "$REPLY" != "y" ]]; then
        exit 1
    fi;
fi

echo "Terminating all connections"
export PGPASSWORD="$POSTGRES_PASSWORD"
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -c  "SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();" || true

echo "Creating new DB"
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS \"$POSTGRES_DB\";"
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER"  -d postgres -c "CREATE DATABASE \"$POSTGRES_DB\";"

echo "Creating schema"
TW_DISABLE_MIGRATIONS=True python3 manage.py migrate --noinput --run-syncdb
python3 manage.py migrate --fake

echo "Loading fixtures"
python3 manage.py loaddata initial

python3 manage.py migrate_from_dump
