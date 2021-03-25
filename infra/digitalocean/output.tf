output "public_ips" {
    value = [
        for o in digitalocean_droplet.cluster:
        [o.name, o.ipv4_address]
    ]
}

output "first_manager_name" {
    value = local.first_manager_name
}

output "first_website_server_name" {
    value = local.first_manager_name  # Does not have to be in general
}

output "manager_names" {
    value = keys(local.managers)
}

output "website_servers_names" {
    value = keys(local.managers)  # Does not have to be in general
}
