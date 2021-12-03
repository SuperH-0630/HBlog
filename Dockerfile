FROM python:3.9-bullseye
WORKDIR /app
COPY . .
RUN ["python", "-m", "pip", "install", "--upgrade", "pip"]
RUN ["python", "-m", "pip", "install", "-r", "requirements.txt"]
EXPOSE 8080
ENTRYPOINT ["python", "main.py"]