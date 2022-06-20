FROM python:3.9.13-buster

RUN mkdir -p /usr/src/app
ENV CONTAINER_HOME=/usr/src/app
ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && apt update && apt install ngrok
RUN pip install pipenv
RUN pipenv install

ENTRYPOINT ["pipenv", "run", "python", "configure_and_run.py", "&"]
