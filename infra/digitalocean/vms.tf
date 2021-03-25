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

locals {
    first_manager_name = "lon-a"
    first_manager_region = "lon1"
    managers = {
        (local.first_manager_name) = local.first_manager_region,
        "lon-b" = "lon1",
        "ams-a" = "ams3",
    }
}

resource "digitalocean_droplet" "cluster" {
    for_each = local.managers

    image = "docker-20-04"
    name = each.key
    region = each.value
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
