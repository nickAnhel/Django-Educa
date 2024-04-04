# Pull python
FROM python:3.11.4

# Set env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /code

# Install dependecies
RUN pip3 install --upgrade pip
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt

# Copy django project
COPY . /code/