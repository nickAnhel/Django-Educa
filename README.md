# Educa

Study project from the book "Django 4 by Example" by Antonio Mele

# Local Launcing

First of all you need to generate SSL certificate using OpenSSL.

```console
md educa/ssl
openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes -keyout ssl/educa.key -out ssl/educa.crt -subj '/CN=*.educaproject.com' -addext 'subjectAltName=DNS:*.educaproject.com'
```

Next you need to up docker project using the following command.

```console
docker compose up
```

Now you need to make migrations for database.

```console
docker compose exec web python3 /code/educa/manage.py migrate
```

Ultimately you need to collect all static files.

```console
docker compose exec web python3 /code/educa/manage.py collect static
```
