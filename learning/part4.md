Change of plans. I don't see a point in having 2 clusters in one data center.
I will start by having 1 in London and 1 in Amsterdam. However Digital Ocean
does not offer cross-center load balancing. I believe I could use AWS's
Route 53 but a simple and hopefully sufficient solution is to create 2 DNS
records and allow clients to do round robin (which I understand to be a
default behavior in common Internet browsers).

The config I have now:

```HCL
variable "do_key_name" {
  sensitive = true
}
variable "do_token" {
  sensitive = true
}
variable "private_key" {
  sensitive = true
}

terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.4.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

data "digitalocean_ssh_key" "terraform" {
  name = var.do_key_name
}

resource "digitalocean_droplet" "cluster" {
    for_each = toset(["lon1", "ams3"])

    image = "ubuntu-20-04-x64"
    name = "cluster-${each.key}"
    region = each.key
    size = "s-1vcpu-1gb"
    private_networking = true
    ssh_keys = [data.digitalocean_ssh_key.terraform.id]

    connection {
        host = self.ipv4_address
        user = "root"
        type = "ssh"
        private_key = var.private_key
        timeout = "2m"
    }

    provisioner "remote-exec" {
        inline = [
            "export PATH=$PATH:/usr/bin",
            "sudo apt update",
            "sudo apt -y install nginx"
        ]
    }
}

resource "digitalocean_domain" "default" {
   name = "metadata.social"
}

resource "digitalocean_record" "CNAME-www" {
  domain = digitalocean_domain.default.name
  type = "CNAME"
  name = "www"
  value = "@"
}

resource "digitalocean_record" "A" {
  for_each = digitalocean_droplet.cluster

  domain = digitalocean_domain.default.name
  type = "A"
  name = "@"
  value = each.value.ipv4_address
}
```

I'll need to split it into separate files.

I like this tool.
