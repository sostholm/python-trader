FROM python:3.8-buster

COPY /src/ /app/

COPY requirements.txt /app/

WORKDIR /app

RUN python3 --version
RUN python3 -m pip install -r requirements.txt
 
CMD ["uvicorn", "app:app", "--ssl-keyfile=/run/secrets/key", "--ssl-certfile=/run/secrets/cert", "--host", "0.0.0.0", "--port", "8000"]