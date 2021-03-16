FROM ubuntu:focal

COPY /src/ /app/

COPY ai_requirements.txt /app/

WORKDIR /app

# RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list
# RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
# RUN apt update
RUN apt-get update
# RUN apt-get install -y python3-tflite-runtime
RUN apt install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y python3.8 python3.8-dev python3.8-distutils python3.8-venv
RUN apt-get install -y python3-pip
RUN apt install python-is-python3
RUN pip3 install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime
RUN python3 --version
RUN python3 -m pip install -r ai_requirements.txt

CMD ["uvicorn", "ai_app:app", "--host", "0.0.0.0", "--port", "8003"]
