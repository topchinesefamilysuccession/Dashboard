# Use Python37
FROM python:3.9

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . .

RUN pip install -r requirements.txt
RUN pip install gunicorn

# Run app.py when the container launches
CMD exec gunicorn --bind :$PORT --log-level info --workers 1 --threads 8 --timeout 0 index:server