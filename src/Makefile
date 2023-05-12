run:
	./manage.py runserver 0.0.0.0:8000

collectstatic:
	./manage.py collectstatic --noinput

migrate:
	./manage.py makemigrations
	./manage.py migrate

test:
	pathon -Wa manage.py test --keepdb

updatedb:
	./manage.py update_db

makemsgs:
		django-admin makemessages -a

compilemsgs:
		django-admin compilemessages --use-fuzzy --locale es

update:
	git fetch
	git pull
	$(MAKE) migrate
	$(MAKE) collectstatic

