FROM python:3.6.12-slim

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY ./wsgi.py /app/
COPY ./cloud_sheep/ /app/cloud_sheep/
WORKDIR /app/

EXPOSE 8000

CMD gunicorn -b 0.0.0.0:8000 wsgi:app
