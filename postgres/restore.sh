#!/bin/sh
pg_restore -d test -U jordan /docker-entrypoint-initdb.d/db.dump
