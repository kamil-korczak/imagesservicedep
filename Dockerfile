FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Upgrade pip and add google packages
RUN pip install --upgrade pip

# Install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD exec gunicorn --bind :8000 --workers 1 --threads 4 --log-level DEBUG imagesservicedep.wsgi:application
