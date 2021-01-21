# Goals

This whole project is a one big learning exercise (with intention of the end
product being useful).

I know very little about popular cloud related tools such as Kubernetes.

Learning wise my goal is to get some familiarity with:

- Terraform
- Kubernetes
- Docker

I would like the application to run in a few, say 3, distinct locations.
This is to have some fault tolerance and to be able to do rolling upgrades.

# Architecture

The data will be fairly static, small and read-only (although ETL
will be required). I think I will distribute copies to all
the nodes such that they have instant, robust access to the data.
The rarely used ETL service will sit in one of the nodes.
Disappointingly simple.

# First steps...

Today and yesterday I read a little about Docker and Kubernetes.
Frankly, I don't know how to even start yet.
I want the first step to be a "Hello world" page running on
a single node. Time to do more reading...
