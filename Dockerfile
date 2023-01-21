# build with: gcloud builds submit --tag gcr.io/PROJECT_ID/IMAGE_NAME
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt --use-deprecated=legacy-resolver

ENV IS_DOCKER_CONTAINER yes


ENTRYPOINT ["python", "main.py"]

