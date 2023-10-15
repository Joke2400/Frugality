ARG WORKDIR="/app"
ARG APPNAME="Frugality"
ARG USERNAME="frugality"

FROM python:3.11.5

ARG vscode
RUN if [[ -z "$devcontainercli" ]] ; then printf "\nERROR: This Dockerfile needs to be built with VS Code !" && exit 1; else printf "VS Code is detected: $devcontainercli"; fi

ARG WORKDIR
ARG APPNAME
ARG USERNAME

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# apt-get update && install && add custom user
RUN apt-get update -y && apt-get install -y --no-install-recommends
RUN adduser --system --group --home ${WORKDIR} ${USERNAME}
USER ${USERNAME}

# Install requirements
WORKDIR /home/${APPNAME}${WORKDIR}
COPY  ./requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Copy files
COPY . .

EXPOSE 80

CMD ["python3", "main.py"]