FROM python:3.6

WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app

EXPOSE 8080

CMD ["python", "-u", "app.py"]