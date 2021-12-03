FROM python:3.9-bullseye
WORKDIR /app
COPY . .
RUN ["python", "-m", "pip", "install", "--upgrade", "pip"]
RUN ["python", "-m", "pip", "install", "-r", "requirements.txt"]
RUN ["python", "-m", "pip", "install", "gunicorn"]
EXPOSE 80
ENTRYPOINT ["python", "-m", "gunicorn", "-c", "./gunicorn.conf.py", "main:app"]