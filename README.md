telesh
======

# What's that
Simple web shell (i.e. tool for executing shell commands on remote hosts) with client-server model: 
remote client are announcing their presence to server that have simple REST API to run commands on
specified host. 

# Requirements
Server uses tornado, so you should install it with pip or distro's package manager. Client uses only python-requests. 

# Usage
Start server:
```bash
./server.py -p 8088
```

Start client, use `-c` to specify allowed commands (regexp, automatically enclosed in ^$):
```bash
./client.py -u http://example.com:8088 -c 'echo \w+' 'uptime' 'ps aux'
```

To run some command on specific host:
```bash
curl -vks -X POST -d '{"action": "run", "value": "echo hello world"}' http://example.com:8088/notify/some-hostname.example.com
```

# FAQ
*  **Q:** Is it safe?  
 **A:** I don't think so. Pretty sure there are some ways to bypass command filter and run `rm -rf`.  


* **Q:** How can I use it?  
 **A:** I don't know. Just don't do anything nasty. Or do - I don't care, to be honest.


