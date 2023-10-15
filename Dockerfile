ARG WORKDIR="/app"
ARG APPNAME="Frugality"
ARG USERNAME="frugality"

FROM python:3.11.5

ARG WORKDIR
ARG APPNAME
ARG USERNAME

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update -y && apt-get install -y --no-install-recommends

RUN adduser --system --group --home ${WORKDIR} ${USERNAME}
USER ${USERNAME}

WORKDIR /home/${APPNAME}${WORKDIR}

COPY ./requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python3", "main.py"]