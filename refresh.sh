#! /bin/sh

if [ "$(pwd)" != /home/appu/appuwrotethese/src/ ]; then
    cd /home/appu/appuwrotethese/src
fi

git pull
pipenv install
pipenv run make migrate
pipenv run make collectstatic

killall gunicorn
sleep 2
pipenv run gunicorn & disown
