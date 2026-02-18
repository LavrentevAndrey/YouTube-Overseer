import socket
import sys

def get_ip_addresses(domain):
    try:
        # Get all info (family, type, proto, canonname, sockaddr)
        # AF_INET for IPv4
        infos = socket.getaddrinfo(domain, None, socket.AF_INET)
        # Extract IP addresses (sockaddr[0])
        ips = set(info[4][0] for info in infos)
        return list(ips)
    except socket.gaierror:
        # sys.stderr.write(f"Could not resolve {domain}\n")
        return []

def main():
    domains = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "googlevideo.com" # Note: main domain only, might not catch all CDNs
    ]
    
    all_ips = set()
    for domain in domains:
        ips = get_ip_addresses(domain)
        all_ips.update(ips)
        
    for ip in all_ips:
        print(ip)

if __name__ == "__main__":
    main()
