run:
	python3 manage.py runserver 0.0.0.0:8000

makemsgs:
		django-admin makemessages -a
	
compilemsgs:
		django-admin compilemessages --use-fuzzy --locale es
	
migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

collectstatic:
	python3 manage.py collectstatic --noinput

updatedb:
	python3 manage.py update_db

update:
	git fetch
	git pull
	$(MAKE) migrate
	$(MAKE) collectstatic
