FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

RUN apt update

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -q -r requirements.txt

COPY . .

CMD ["bash", "./entrypoint.sh"]