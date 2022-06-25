FROM python:3

RUN mkdir -p /opt/src/applications
#RUN mkdir -p /opt/src/applications/customer
WORKDIR /opt/src/applications

COPY applications/customer/application.py ./application.py
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/applications"

ENTRYPOINT ["python", "./application.py"]