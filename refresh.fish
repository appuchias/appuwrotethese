#! /usr/bin/fish

if [ "(pwd)" != /home/appu/appuwrotethese/src/ ]
    cd /home/appu/appuwrotethese/src
end

pipenv run make update

# sudo reboot

killall gunicorn && pipenv run gunicorn & disown
