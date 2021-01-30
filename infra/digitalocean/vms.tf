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
