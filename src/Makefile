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

lesscompile: # Install AUR: nodejs-less and nodejs-less-plugin-clean-css
	lessc staticfiles/styles/styles.less staticfiles/styles/styles.min.css --clean-css
	lessc staticfiles/styles/project_styles.less staticfiles/styles/project_styles.min.css --clean-css

update:
	git fetch
	git pull
	$(MAKE) migrate
	$(MAKE) collectstatic

