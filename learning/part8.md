Turns out that `docker-compose` is a port of a 3rd part tool:
https://orchardup.github.io/fig.sh/

These days we also have `docker stack`:
https://docs.docker.com/engine/reference/commandline/stack/

It's a native tool, uses a similar configuration file
and `compose` and `stack` have a large common set of commands:
https://docs.docker.com/compose/compose-file/compose-file-v3/

Also stack can be used to define Swarm behaviour.
Looks like docker-compose is on the legacy part of things. Thus I will be
using `stack`.

As a side note: in my opinion Docker documentation is very messy. I had a look
at its source repository. It looks like it's been growing organically for
years without strongly imposing structure and some things are in odd places.
For example this page
https://docs.docker.com/engine/swarm/stack-deploy/
is not even linked directly to the rest of the documentation which has
section about swarm. I do find it puzzling. With docker being so widespread
- can't they produce a decent documentation?

Anyway... I managed to create a 3-node swarm with each node being a manager
and a worker. They all are identical replicas in 3 different data centers.

Serving over https was more cumbersome than expected.
I'm using `Let's Encrypt` CA. In one node, non-containerized deployment one can
just use Certbot: https://certbot.eff.org/ which can obtain the certificate
and even reconfigure our web server. And take care of renewals!

With 1 node containerized deployment things get more difficult, because
Certbot can't reach our web server. There are instructions: 
https://certbot.eff.org/docs/install.html#running-with-docker

But what if we have multiple nodes? And we want them to be ephemeral.

I decided to obtain the certificate manually and go with DNS challenge
(https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) rather than
HTTP-01 and manually copy the relevant file to all the nodes.
I do not have automatic renewal set up in any way and I suspect I will not be
working on it in the foreseeable future. 

In any case... I have a swarm running with nodes in 3 different data centers
serving "content" (which is not far from a blank page) over https.
One of my issues now is lack of non-production environment. My plan is to set
it up when I am near having a minimal viable product. Because until then I
could argue that I don't have a production environment...

There are still some rough edges I need to smooth of before starting
the development of the content. Specifically I am very much not happy with
how I deploy and version my images.

One more thing. There's this nice tool that can help configure web server
for https: https://ssl-config.mozilla.org/
