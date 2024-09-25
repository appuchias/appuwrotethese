# syntax=docker/dockerfile:1.7-labs

FROM python:3.12-bookworm
WORKDIR /usr/local/awt

# Install the system dependencies
RUN apt update && apt install -y cron

# Install the application dependencies
COPY requirements.txt ./
# ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Setup a webapp user so the container doesn't run as the root user
RUN useradd awt
USER awt

# Copy in the source code
# COPY --exclude=db.sqlite3 src ./src
ADD --chown=awt:awt src ./src
RUN touch /usr/local/awt/src/db.sqlite3

# Set the environment variables
ENV HTTPS=false
ENV PROD=true

# Run the application
WORKDIR /usr/local/awt/src
RUN echo "ALLOWED_HOSTS += ['*']" >> ./appuwrotethese/settings.py && \
    python manage.py collectstatic --noinput && \
    python manage.py migrate
# RUN python manage.py migrate

# Expose the port
EXPOSE 80

# Setup the cron job
USER root
COPY crontab /usr/local/awt/crontab
RUN chown awt:awt /usr/local/awt/crontab && \
    chmod 0644 /usr/local/awt/crontab && \
    crontab -u awt /usr/local/awt/crontab
# RUN chmod 0644 /usr/local/awt/crontab
# RUN crontab -u awt /usr/local/awt/crontab

# Setup cron log
RUN touch /var/log/cron.log
RUN chown awt:awt /var/log/cron.log
 
USER root
CMD cron && su - awt -c "HTTPS=$HTTPS PROD=$PROD gunicorn"
