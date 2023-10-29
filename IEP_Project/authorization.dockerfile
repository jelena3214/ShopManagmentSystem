FROM python:3

RUN mkdir -p /opt/src/authorization
WORKDIR /opt/src/authorization

COPY authorization/application.py ./application.py
COPY authorization/configuration.py ./configuration.py
COPY authorization/models.py ./models.py
COPY authorization/requirements.txt ./requirements.txt
COPY authorization/functions.py ./functions.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authorization"

ENTRYPOINT ["python", "./application.py"]
