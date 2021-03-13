FROM intel/intel-optimized-tensorflow

COPY /src/ /app/

COPY ai_requirements.txt /app/

WORKDIR /app

RUN apt update
RUN apt install -y libgl1-mesa-glx
RUN python3 --version
RUN python3 -m pip install -r ai_requirements.txt

CMD ["uvicorn", "ai_app:app", "--host", "0.0.0.0", "--port", "8003"]
