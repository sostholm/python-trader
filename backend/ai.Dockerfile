FROM python:3.8-buster

COPY /src/ /app/

COPY ai_requirements.txt /app/

WORKDIR /app

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt update
RUN apt-get -y install python3-tflite-runtime
RUN apt install -y libgl1-mesa-glx
RUN python3 --version
RUN python3 -m pip install -r ai_requirements.txt

CMD ["uvicorn", "ai_app:app", "--host", "0.0.0.0", "--port", "8003"]
