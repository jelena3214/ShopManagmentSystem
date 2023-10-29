FROM python:3

RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

COPY store/applicationCourier.py ./applicationCourier.py
COPY store/configuration.py ./configuration.py
COPY store/models.py ./models.py
COPY store/requirementsv2.txt ./requirements.txt
COPY sources /sources
COPY keys.json ./keys.json

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/store"

ENTRYPOINT ["python", "./applicationCourier.py"]
