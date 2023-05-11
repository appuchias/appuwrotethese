run:
	python3 manage.py runserver 0.0.0.0:8000

collectstatic:
	python3 manage.py collectstatic --noinput

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

test:
	python3 manage.py test

updatedb:
	python3 manage.py update_db

makemsgs:
		django-admin makemessages -a

compilemsgs:
		django-admin compilemessages --use-fuzzy --locale es

update:
	git fetch
	git pull
	$(MAKE) migrate
	$(MAKE) collectstatic

