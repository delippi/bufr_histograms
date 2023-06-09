#!/bin/bash
if [ $# != 2 ]; then
  echo "usage: incdate YYYYMMDDHH hrs"
  echo "where YYYYMMDDHH is a 10 character date string (e.g. 2002050312)"
  echo "and hrs is integer number of hours to increment YYYMMDDHH"
  exit 1
fi
date -u -d "${1:0:4}-${1:4:2}-${1:6:2} ${1:8:2}:00:00 UTC $2 hour" +%Y%m%d%H

