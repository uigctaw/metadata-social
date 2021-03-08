Haven't been spending a lot of time on this project recently... Time to get
back to it. Still, I managed to deploy an nginx + Python app that updates
index.html file with random number every few seconds. Seems to work.

docker-compose.yaml
```yaml
version: "3.7"
services:
  backend:
    image: uigctaw/metadata-social:nginx-test
    volumes:
      - myapp:/usr/share/nginx/html
    ports:
     - 8080:80
  app:
    image: uigctaw/metadata-social:pyapp
    volumes:
      - myapp:/app
volumes:
    myapp:
```

nginx Dockerfie:
```
FROM nginx
COPY my\_html /usr/share/nginx/html
```

Python program Dockerfile:
```
FROM python:3.8-slim-buster
COPY app.py .
CMD [ "python3", "app.py"]
```

app.py:
```python
import random
import time


if __name__ == '__main__':
    while True:
        with open('app/index.html', 'w') as fh:
            fh.write(str(random.random()))
        time.sleep(random.random() * 10 + 1)
```


Not very advanced stuff but I'm happy I achieved this small milestone.

I've done some reading about Docker Swarm. Quite conveniently it comes with
the Docker package and the system can be defined using a Compose file.
