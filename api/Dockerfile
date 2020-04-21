FROM python:3.6
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY /src /app
WORKDIR /app
EXPOSE 8081
CMD ["python", "-u", "main.py"]
