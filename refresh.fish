#! /usr/bin/fish

if [ "(pwd)" != /home/appu/appuwrotethese/src/ ]
    cd /home/appu/appuwrotethese/src
end

pipenv install

pipenv run make update

killall gunicorn
sleep 2
pipenv run gunicorn & disown
