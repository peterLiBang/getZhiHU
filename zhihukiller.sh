#!/bin/bash
kill -9 $(ps -ef | grep get_user.py | gawk '$0 !~/grep/ {print $2}' | tr -s '\n' ' ')
kill -9 $(ps -ef | grep consumer.py | gawk '$0 !~/grep/ {print $2}' | tr -s '\n' ' ')

