FROM python:3.8

WORKDIR /bottle-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./ ./app

CMD "foreman start -m gateway=1,users=1,timelines=3,user-queries=1,timeline-queries=1,direct-messages=1,search-engine=1,message-queue=1,dynamoDB=1,redis=1,worker=1"