# see https://hub.docker.com/_/python/
FROM python:3.5.0-slim

# Prepare the environment
RUN pip install --no-cache --upgrade pip
RUN mkdir /app
COPY LICENSE /app/
COPY requirements.txt /app/

# install the environment
RUN cd /app && \
    pip install --no-cache -r requirements.txt

COPY first_timer_scaper /app/first_timer_scraper

# Prepare execution
EXPOSE 80
WORKDIR /app/
ENV PYTHONUNBUFFERED 0
VOLUME ["/app/secret", "/app/model"]

ENTRYPOINT ["python3", "-m", "first_timer_scraper.app"]
CMD ["/tmp/cache", "/app/secret", "/app/model"]
