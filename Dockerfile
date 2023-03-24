FROM python:3

# install cron
RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# copy and install cronjob
COPY api_cron /etc/cron.d/api_cron
RUN chmod 0644 /etc/cron.d/api_cron && touch /var/log/cron.log && crontab /etc/cron.d/api_cron

ENV TZ=America/Mexico_City

CMD cron -f && tail -f /var/log/cron.log
