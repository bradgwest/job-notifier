FROM python:3.12-alpine

RUN apk -qq update \
    && python -m pip install --upgrade pip

COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

COPY download.py /opt/download.py

ENTRYPOINT ["python", "/opt/download.py"]
CMD ["--help"]
