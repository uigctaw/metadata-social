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
