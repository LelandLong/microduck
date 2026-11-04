import socket, json, sys
s = socket.create_connection(("127.0.0.1", 7801)); f = s.makefile("rw")
f.write(json.dumps({"op": "hello", "protocol": 1, "joints": 15}) + "\n"); f.flush(); f.readline()
f.write(json.dumps({"op": "read"}) + "\n"); f.flush(); r = json.loads(f.readline()); print(*[round(v, 3) for v in r["trunk"][:3]])
