FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TZ=America/Mexico_City

CMD ["/bin/sh", "-c", "python api.py && python join_table.py"]
