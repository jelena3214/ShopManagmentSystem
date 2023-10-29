FROM python:3

RUN mkdir -p /opt/src/init
WORKDIR /opt/src/init

COPY keys.json ./keys.json
COPY accountsInit.py ./accountsInit.py
COPY store/requirementsv2.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/init"

ENTRYPOINT ["python", "./accountsInit.py"]
