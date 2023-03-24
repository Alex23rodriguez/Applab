FROM python:3

WORKDIR /usr/src/app

COPY python/requirements.txt ./python/requirements.txt

RUN pip install --no-cache-dir -r python/requirements.txt

COPY . .

ENV TZ=America/Mexico_City

CMD ["/bin/sh", "-c", "python api.py && python join_tables.py"]
