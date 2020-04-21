FROM python:3.6

WORKDIR /adapter

COPY requirements.txt /adapter
RUN pip install -r requirements.txt

COPY main.py /adapter
CMD ["python", "-u", "main.py"]
