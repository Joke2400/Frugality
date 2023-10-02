FROM python:3.11.5

WORKDIR /src

COPY ./requirements.txt /src
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /src

CMD ["uvicorn", "main:process.app", "--host", "0.0.0.0", "--port", "80"]