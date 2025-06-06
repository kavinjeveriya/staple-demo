FROM python:3.10-slim

WORKDIR /app

COPY app.py  requirements.txt /app/

RUN pip install -r requirements.txt

RUN mkdir -p /var/staple-demo/logs

RUN chmod -R 777 /var/staple-demo/logs

EXPOSE 5000

CMD ["python", "app.py"]
