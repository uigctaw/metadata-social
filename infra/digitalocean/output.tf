output "public_ips" {
    value = [
        for o in digitalocean_droplet.cluster:
        [o.name, o.ipv4_address]
    ]
}
