# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app
COPY mtg-cards-consumer.py /app
COPY mtg-sets-consumer.py /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y cron

RUN echo "0 8 * * * /usr/local/bin/python /app/mtg-cards-consumer.py >> /var/log/cron.log 2>&1" > /etc/cron.d/mtg-cards-consumer && \
    chmod 0644 /etc/cron.d/mtg-card-sync && \
    crontab /etc/cron.d/mtg-card-sync && \
    touch /var/log/cron.log

RUN echo "30 8 * * * /usr/local/bin/python /app/mtg-sets-consumer.py >> /var/log/cron.log 2>&1" > /etc/cron.d/mtg-sets-consumer && \
    chmod 0644 /etc/cron.d/mtg-card-sync && \
    crontab /etc/cron.d/mtg-card-sync && \
    touch /var/log/cron.log

# Ensure cron runs in the foreground
#CMD ["cron", "-f"]
CMD ["tail", "-f", "/dev/null"]
