FROM python:3.11-slim
# Use 3.11 to avoid django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 or psycopg module
LABEL org.opencontainers.image.authors="Julian-Samuel Gebühr"

ENV DOCKER_BUILD=true

RUN apt update
RUN apt install gettext -y
RUN apt install libpq-dev gcc -y
COPY . /app
WORKDIR /app
RUN mkdir /app/data
RUN mkdir /app/data/static
RUN mkdir /app/data/media
RUN pip install -e .  # Without the -e the library static folder will not be copied by collectstatic!

RUN nf collectstatic --noinput
RUN nf compilemessages --ignore venv

COPY docker/notfellchen.bash /bin/notfellchen

EXPOSE 7345
CMD ["notfellchen"]
