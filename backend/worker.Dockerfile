FROM python:3.8-buster

COPY /src/ /app/

COPY requirements.txt /app/

WORKDIR /app

RUN python3 --version
RUN python3 -m pip install -r requirements.txt

CMD ["uvicorn", "runners_app:app", "--port", "8002"]