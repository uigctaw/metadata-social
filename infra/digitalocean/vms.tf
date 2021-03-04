terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.5.1"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_ssh_key" "main" {
  name = var.do_key_name
  public_key = file(var.public_key_path)
}

resource "digitalocean_droplet" "cluster" {
    for_each = toset(["lon1", "ams3"])

    image = "docker-20-04"
    name = "cluster-${each.key}"
    region = each.key
    size = "s-1vcpu-1gb"
    private_networking = true
    ssh_keys = [digitalocean_ssh_key.main.fingerprint]
    user_data = templatefile(
        "${path.module}/cloud_init.yaml",
        {
            droplet_uname = var.droplet_uname,
            public_key = digitalocean_ssh_key.main.public_key,
        }        
    )
}
