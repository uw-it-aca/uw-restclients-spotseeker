ARG DJANGO_CONTAINER_VERSION=1.4.1

FROM gcr.io/uwit-mci-axdd/django-container:${DJANGO_CONTAINER_VERSION} as app-container

USER acait

ADD --chown=acait:acait ./setup.py /app/

ADD --chown=acait:acait ./docker/test-app/test_app/ /app/test_app
ADD --chown=acait:acait ./uw_spotseeker/ /app/uw_spotseeker/

ADD --chown=acait:acait ./docker/settings.py /app/project/
ADD --chown=acait:acait ./docker/urls.py /app/project/

WORKDIR /app/

RUN . /app/bin/activate && pip install .
RUN /app/bin/python manage.py migrate
