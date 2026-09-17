FROM python:3.9-slim-bullseye
RUN apt-get update
RUN pip3 install rpyc redis
CMD [ "/bin/bash", "-c", "while true; do bash -l; done" ]