import docker

def get_client(ip):
    print(ip)
    tls_config = docker.tls.TLSConfig(client_cert=('/var/lib/certs/ssl/cert.pem', '/var/lib/certs/ssl/key.pem'))
    return docker.DockerClient(base_url=f'https://{ip}:2376/', tls=tls_config)
