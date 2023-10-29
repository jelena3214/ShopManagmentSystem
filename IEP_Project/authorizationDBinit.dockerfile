FROM python:3

RUN mkdir -p /opt/src/authorization
WORKDIR /opt/src/authorization

COPY authorization/migrate.py ./migrate.py
COPY authorization/configuration.py ./configuration.py
COPY authorization/models.py ./models.py
COPY authorization/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
ENTRYPOINT ["python", "./migrate.py"]
