FROM python:3.9-slim-bullseye
RUN apt-get update
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "/bin/bash", "-c", "while true; do bash -l; done" ]