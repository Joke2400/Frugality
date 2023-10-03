FROM mcr.microsoft.com/devcontainers/universal:2-linux

RUN apt-get install -y && apt-get upgrade -y

WORKDIR /usr/src/

COPY ./requirements.txt /usr/src/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /usr/src/
CMD ["uvicorn", "main:process.app", "--host", "0.0.0.0", "--port", "80"]