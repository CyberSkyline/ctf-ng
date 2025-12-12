#!/bin/bash

# Setup default drop
iptables -I DOCKER-USER -j DROP

function allow() {
    iptables -I DOCKER-USER -s $1 -j ACCEPT
    iptables -I DOCKER-USER -d $1 -j ACCEPT
}

# Allow private network address spaces
iptables -I DOCKER-USER -s 192.168.0.0/16 -j ACCEPT
iptables -I DOCKER-USER -s 172.16.0.0/12 -j ACCEPT
iptables -I DOCKER-USER -s 10.0.0.0/8 -j ACCEPT

# Allow google dns
allow '8.8.8.8'


while read host; do
    allow $host;
done <hosts.txt
