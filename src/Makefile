run:
	./manage.py runserver 0.0.0.0:8000

collectstatic:
	./manage.py collectstatic --noinput

migrate:
	./manage.py makemigrations
	./manage.py migrate

test:
	python -Wa manage.py test --keepdb

updatedb:
	./manage.py update_db

makemsgs:
		django-admin makemessages -a

compilemsgs:
		django-admin compilemessages --use-fuzzy --locale es

lesscompile:
	lessc staticfiles/res/styles.less staticfiles/res/styles.css
	lessc staticfiles/res/project_styles.less staticfiles/res/project_styles.css

update:
	git fetch
	git pull
	$(MAKE) migrate
	$(MAKE) collectstatic

