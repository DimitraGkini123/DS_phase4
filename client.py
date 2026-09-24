import os
import rpyc
import time
import random
import threading

from dataclasses import dataclass 

"""======================================================================================================================================"""
deleteClosedRequests = False
requestRate = 50
numRequests = 1000
"""======================================================================================================================================"""

@dataclass
class request:
    reqID: int
    keyword: str
    text: str  
    response: int = -1  
    e2eTime: int = -1


req: list[request] = []          #list of requests sent
req_lock = threading.Lock()      #protects req list from race conditions
currID = 0


words: list[str] = ["cow", "sheep", "now", "then", "the", "end", "out", "eagle", "Monday", "geometry", "find", "crowd", "and", "time", "place", "go", "just", "minutes", "hours", "plug", "victory", "enemy", "friend", "ally", "we", "straight", "corner", "run", "attempt", "defeat", "failure", "welcome", "lap", "music", "goodbye", "come", "leave", "my", "your", "you", "he", "she", "puts", "takes", "gives", "look", "see", "visit", "need", "weekend", "gone", "option", "moment", "band", "stage", "glove", "stone", "power", "energy", "someone", "seconds", "first", "second", "man", "woman", "red", "black", "blue", "white", "green", "yellow", "white", "purple", "brown", "dark", "light", "orange", "tree", "plant", "flower", "read", "reality", "walk", "drive", "car", "plane", "bike", "bicycle", "bus", "taxi", "helicopter", "boat", "ship", "vehicle", "transport", "move", "engage", "miss", "hit", "sing", "song", "cat", "dog", "shop", "buy", "sell", "make", "break", "fix", "repair", "on", "in", "at", "over", "under", "begin", "end", "study", "code", "cable", "wire", "speak", "deal", "feel", "touch", "smell", "taste", "ice", "fire", "water", "earth", "moon", "stars", "mars", "sun", "sea", "wall", "paint", "sword", "gun", "weapon", "pistol", "bullet", "fuse", "connect", "disconnect", "lamp", "switch", "route", "way", "road", "street", "sidewalk", "market", "mall", "city", "town", "country", "nation", "village", "person", "citizen", "die", "live", "health", "happy", "sad", "dirty", "clean", "poor", "rich", "pizza", "souvlaki", "cream", "fresh", "old", "new", "juice", "wine", "soda", "cola", "milk", "shake", "milkshake", "coffee", "chocolate", "cake", "bread", "salt", "pepper", "mint", "tooth", "breath", "air", "wind", "windy", "calm", "angry", "rain", "thunder", "storm", "thunderstorm", "hail", "lightning", "cloud", "cloudy", "station", "master", "key", "lock", "smith", "supply", "demand", "blood", "bone", "bones", "mind", "soul", "body", "hand", "legs", "face", "nose", "mouth", "ears", "lips", "pad", "table", "tower", "wizard", "knight", "gate", "knights", "gates", "tables", "pads", "parking", "garage", "home", "house", "return", "trip"]
fileNames: list[str] = []


def readAvailableFileNames():
    global fileNames
    fileNames = os.listdir("SampleTexts")         #read every file name in the folder
    fileNames = [name[:-4] for name in fileNames]     #remove .txt


def newRequest() -> request:
    global currID
    r = request(
        reqID=currID,                             #assign the next id
        keyword=random.choice(words),             #random word from list
        text=random.choice(fileNames),            #random text file from folder
        e2eTime=time.time_ns() // 1000,           #request creation time in μs
    )
    with req_lock:                                #lock while modifying the shared list
        req.append(r)                             #append request to the list
    currID += 1                                   #increment id
    return r


def closeRequest(id:int, resp:int):
    with req_lock:
        if deleteClosedRequests:
            for i in range(len(req) - 1, -1, -1):
                if req[i].reqID == id:
                    r = req.pop(i)
                    r.response = resp
                    r.e2eTime = (time.time_ns() // 1000) - r.e2eTime
                    return r
        else:
            for r in reversed(req):
                if r.reqID == id:
                    r.response = resp
                    r.e2eTime = (time.time_ns() // 1000) - r.e2eTime
                    return r
    #no fail protection, not needed but should exist


def receiveResponse(async_result, done_sem: threading.Semaphore):
    id, resp = async_result.value           #unpack the id and response sent back by the server
    r = closeRequest(id, resp)              #close the request and get its data to print them
    
    print(f"id={r.reqID} keyword={r.keyword} text={r.text} "
          f"response={r.response} latency={r.e2eTime / 1000:.2f}ms")
    done_sem.release()                      #wake up main thread's wait-count by one


def sendRequests(async_count, rate_hz: float, done_sem: threading.Semaphore, num_requests: int):
    interval = 1.0 / rate_hz                      #time between requests
    next_send = time.perf_counter()               #scheduled time for the next send

    for _ in range(num_requests):
        r = newRequest()                                        #creates a new request and stores it in req[]
        async_result = async_count(r.reqID, r.keyword, r.text)  #sends the request, non-blocking (returns instantly)
        async_result.add_callback(
            lambda ar, s=done_sem: receiveResponse(ar, s)       #hand off response handling to receiveResponse
        )

        next_send += interval                     #next send time
        sleep_time = next_send - time.perf_counter()
        if sleep_time > 0:                        #only sleep if we're ahead of schedule
            time.sleep(sleep_time)                #wait until it's time for the next request


def main():
    readAvailableFileNames()

    conn = rpyc.connect(os.getenv("SERVER_HOST", "server1"), 18861)          #open connection to the server using rpyc
    rpyc.BgServingThread(conn, serve_interval=0.1, sleep_interval=0)                    #background thread that lets callbacks fire as replies arrive

    async_count = rpyc.async_(conn.root.count)    #wrap the remote method so calls return immediately
    done_sem = threading.Semaphore(0)             #starts at 0; each response releases it once

    sendRequests(async_count, requestRate, done_sem, numRequests)   #fire off all requests

    while True:
        pass


if __name__ == "__main__":
    main()