I seem not to have mentioned one important thing in the previous parts...
I decided not to use Kubernetes and go with Docker swarm. I was surprised
by the level of complexity that comes with Kubernetes. I am not convinced
that using Kubernetes necessarily makes sense at scales other than large
or very large. I wouldn't want to use significantly preconfigured
out-of-the-box Kubernetes deployments to avoid vendor lock-in. And I
wouldn't like to spend time and resources on deploying and configuring it
myself. I'd say that in case of this project even Docker swarm is excessive.
More than that: containers are excessive. But given that it's a learning
project I allow myself to have a bit of unnecessary infrastructure, but
going for Kubernetes just feels too much.

I also need to retract what I said about forgoing `docker-compose` in favor
of `docker stack`. I do use `compose` a lot for local testing.
