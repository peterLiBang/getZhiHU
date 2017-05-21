#!/bin/bash
pkill -9 python
echo 'del already_get_user' | redis-cli
echo 'del user_queue' | redis-cli
echo 'del prepare_user_queue' | redis-cli
echo 'del last_url_map' | redis-cli
echo 'use libq ;delete from FOLLOWERS;' | mysql -uroot -p123456
echo 'use libq ;delete from USERINFO;' | mysql -uroot -p123456
