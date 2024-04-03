pythom3 -m venv .venv
pip3 install -r requirements.txt

docker pull redis
docker run -it --rm --name redis -p 6379:6379 redis