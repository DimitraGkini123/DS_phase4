import rpyc
import time

from dataclasses import dataclass

class request:
    reqID: int
    keyword: str
    text: str
    e2eTime: int
    response: int

req: list[request] = []
currID = 0

def newRequest():
    
    req.append(request(
        reqID=currID,
        keyword="hello",
        text="hello world",
        e2eTime=-1
        response = -1
    ))

    currID=currID+1

def main():
    #initializes rpyc connection to server1 on port 18861
    conn = rpyc.connect("server1", 18861)

if __name__ == "__main__":
    main()


#calls function count on the server with arguments 
result = conn.root.count("keyword", "file.txt")

#closes the connection
conn.close()