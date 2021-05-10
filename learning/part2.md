I read a bit about Terraform.

Now my understanding is:

- Terraform abstracts various cloud providers' APIs
- Kubernetes manages container based services
- Docker is just containers i.e. specially isolated processes

So now for this particular projects this is what I currently imagine as
tasks for these 3 tools.

## Terraform:

- Create Virtual Machines in designated locations
- Add, remove, resize them as needed
- Provide API for Kubernetes? Or will Kubernetes be controlled by Terraform?
  We'll see.
- Also TLS certificate management goes here I suppose

I do not expect this to be part of CI/CD. Whilst it would be nice
to be able to automatically manage resources based on application usage,
for the simple case I have I don't image I'll want to spend time and resources
on this particular piece of automation given its expected low utility.

One important thing to remember is that I do not want to use any provider
specific features to avoid vendor lock-in. At least for now, I am planning to
use Digital Ocean. But if for whatever reason I would like to move to a 
different provider I want Terraform to make it a low effort operation.

## Kubernetes

I want to say something like:

"Kubernetes please use this load balancer to split traffic between
clusters in regions UK1, UK2, UK3. Each cluster should run
services s1, s2, .. sn. Each service is a bunch of containers, such that
s1 = c11, c12, ...; s2 = c21, c22, ...; sn = cn1, cn2, ..."

Kubernetes will be a part of CI/CD pipeline responsible for rolling upgrades.

## Docker

Container building and maintaining. Part of CI/CD.

----

So what are the first steps? I believe it will be Terraform + Docker.
I'm thinking the script should be:

1) Terraform: create a VM.
2) Docker:

    - Fetch a container with a web server (I'll pick nginx).
    - Configure nginx and serve a "Hello world" page.
