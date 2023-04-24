#!/usr/bin/fish

if [ "(pwd)" != /home/appu/appuwrotethese/ ]
    cd /home/appu/appuwrotethese
end

pipenv run make update

# sudo reboot

killall gunicorn && pipenv run gunicorn & disown
