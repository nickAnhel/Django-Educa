pythom3 -m venv .venv
pip3 install -r requirements.txt

docker pull memcached
docker run -it --rm --name memcached -p 11211:11211 memcached -m 64