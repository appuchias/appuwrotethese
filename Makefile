run:
	python3 src/manage.py runserver 0.0.0.0:8000

makemsgs:
	cd src
	django-admin makemessages -a
	cd ..

compilemsgs:
	cd src
	django-admin compilemessages --use-fuzzy --locale es
	cd ..

migrate:
	python3 src/manage.py makemigrations
	python3 src/manage.py migrate

collectstatic:
	python3 src/manage.py collectstatic --noinput

updatedb:
	python3 src/manage.py update_db

update:
	git fetch
	git pull
	$(MAKE) migrate
	$(MAKE) collectstatic
