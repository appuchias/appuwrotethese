FROM python:3.12-bookworm
WORKDIR /awt

# Install the system dependencies
RUN apt update && apt install -y cron

# Setup the cron job
RUN echo 'PATH=/usr/local/bin:$PATH' > tmpcron
RUN echo '' >> tmpcron
RUN echo '@reboot   	su - awt -c "cd /awt/src && python3.12 manage.py update_db --update >> /var/log/cron.log 2>&1"' >> tmpcron
RUN echo '5 * * * *	su - awt -c "cd /awt/src && python3.12 manage.py update_db --update >> /var/log/cron.log 2>&1"' >> tmpcron
RUN echo '5 0 * * 1	su - awt -c "cd /awt/src && python3.12 manage.py clean_games >> /var/log/cron.log 2>&1"' >> tmpcron
RUN crontab tmpcron
RUN rm tmpcron

RUN touch /var/log/cron.log

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Setup a webapp user so the container doesn't run as the root user
RUN useradd --home-dir=/awt awt
USER awt

# Copy in the source code
# COPY --exclude=db.sqlite3 src ./src
ADD --chown=awt:awt src ./src
RUN touch /awt/src/db.sqlite3

# Run the application
WORKDIR /awt/src
RUN echo "ALLOWED_HOSTS += ['*']" >> ./appuwrotethese/settings.py && \
    python manage.py collectstatic --noinput && \
    python manage.py migrate

# Expose the port
EXPOSE 80

# Cron starts everything
USER root
# CMD cron && tail -F /var/log/cron.log
CMD cron && su - awt -c "cd /awt/src && HTTPS=$HTTPS PROD=true gunicorn"
