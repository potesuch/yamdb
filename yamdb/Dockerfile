FROM python:3.10-slim
RUN mkdir /app
COPY yamdb/requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY . /app
WORKDIR /app
CMD ["gunicorn", "yamdb.yamdb.wsgi:application", "--bind", "0:8000"]
