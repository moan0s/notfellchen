FROM python:3-slim
MAINTAINER Julian-Samuel Gebühr

ENV DOCKER_BUILD=true

RUN apt update
RUN apt install gettext -y
COPY . /app
WORKDIR /app
RUN mkdir /app/static
RUN mkdir /app/media
RUN pip install -e .  # Without the -e the library static folder will not be copied by collectstatic!

RUN nf collectstatic --noinput
RUN nf compilemessages --ignore venv

COPY docker/notfellchen.bash /bin/notfellchen

EXPOSE 8345
CMD ["notfellchen"]
