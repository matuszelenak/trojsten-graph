#!/usr/bin/env bash
set -e

export PGUSER="${PGUSER:-graph}"
export PGDATABASE="${PGDATABASE:-graph}"

env | grep '^PG'

if [[ ! -z "$PGHOST" && "$PGHOST" != "localhost" &&  "$PGHOST" != "127.0.0.1" ]]; then
    echo
    read -p "Going to DROP the database on $PGHOST. Continue? [y/N]: "

    if [[ "$REPLY" != "y" ]]; then
        exit 1
    fi;
fi

echo "Terminating all connections"
psql -c "SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();" || true

echo "Creating new DB"
psql -d postgres -c "DROP DATABASE IF EXISTS \"$PGDATABASE\";"
psql -d postgres -c "CREATE DATABASE \"$PGDATABASE\";"

echo "Creating schema"
TW_DISABLE_MIGRATIONS=True python3 manage.py migrate --noinput --run-syncdb
python3 manage.py migrate --fake

echo "Loading fixtures"
python3 manage.py loaddata initial

python3 manage.py migrate_from_dump
