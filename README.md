md educa/ssl
openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes -keyout ssl/educa.key -out ssl/educa.crt -subj '/CN=*.educaproject.com' -addext 'subjectAltName=DNS:*.educaproject.com'

docker compose up
