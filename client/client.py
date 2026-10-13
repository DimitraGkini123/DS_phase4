import os
import csv
import rpyc
import time
import random
import threading

from dataclasses import dataclass 

"""======================================================================================================================================"""
deleteClosedRequests = False    #set to TRUE for long tests - side effect: will disable latency logs
exportLogs = True
requestRate = int(os.getenv("REQUEST_RATE", "1"))
numRequests = int(os.getenv("NUM_REQUESTS", "10000"))
rollingAveragePeriod = 3        #defines the period of the rolling average latency
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


words: list[str] = ["cow", "sheep", "now", "then", "the", "end", "out", "eagle", "Monday", "geometry", "find", "crowd", "and", "time", "place", "go", "just", "minutes", "hours", "plug", "victory", "enemy", "friend", "ally", "we", "straight", "corner", "run", "attempt", "defeat", "failure", "welcome", "lap", "music", "goodbye", "come", "leave", "my", "your", "you", "he", "she", "puts", "takes", "gives", "look", "see", "visit", "need", "weekend", "gone", "option", "moment", "band", "stage", "glove", "stone", "power", "energy", "someone", "seconds", "first", "second", "man", "woman", "red", "black", "blue", "white", "green", "yellow", "purple", "brown", "dark", "light", "orange", "tree", "plant", "flower", "read", "reality", "walk", "drive", "car", "plane", "bike", "bicycle", "bus", "taxi", "helicopter", "boat", "ship", "vehicle", "transport", "move", "engage", "miss", "hit", "sing", "song", "cat", "dog", "shop", "buy", "sell", "make", "break", "fix", "repair", "on", "in", "at", "over", "under", "begin", "study", "code", "cable", "wire", "speak", "deal", "feel", "touch", "smell", "taste", "ice", "fire", "water", "earth", "moon", "stars", "mars", "sun", "sea", "wall", "paint", "sword", "gun", "weapon", "pistol", "bullet", "fuse", "connect", "disconnect", "lamp", "switch", "route", "way", "road", "street", "sidewalk", "market", "mall", "city", "town", "country", "nation", "village", "person", "citizen", "die", "live", "health", "happy", "sad", "dirty", "clean", "poor", "rich", "pizza", "souvlaki", "cream", "fresh", "old", "new", "juice", "wine", "soda", "cola", "milk", "shake", "milkshake", "coffee", "chocolate", "cake", "bread", "salt", "pepper", "mint", "tooth", "breath", "air", "wind", "windy", "calm", "angry", "rain", "thunder", "storm", "thunderstorm", "hail", "lightning", "cloud", "cloudy", "station", "master", "key", "lock", "smith", "supply", "demand", "blood", "bone", "bones", "mind", "soul", "body", "hand", "legs", "face", "nose", "mouth", "ears", "lips", "pad", "table", "tower", "wizard", "knight", "gate", "knights", "gates", "tables", "pads", "parking", "garage", "home", "house", "return", "trip", "emotion", "grab", "jump", "today", "yesterday", "ghost", "spirit", "trash", "floor", "countryside", "vent", "breeze", "gust", "pollen", "bee", "honey", "honeycomb", "copper", "silver", "gold", "diamond", "platinum", "iron", "bronze", "statue", "brother", "sister", "nephew", "relative", "absolute", "alcohol", "beer", "ale", "alley", "cavern", "ancient", "ruins", "behind", "front", "stunned", "grip", "column", "row", "count", "lord", "lady", "mister", "observe", "infer", "bishop", "rook", "pawn", "queen", "chess", "checkers", "board", "direct", "director", "rector", "university", "school", "teacher", "student", "govern", "governor", "government", "institution", "soldier", "warrior", "titan", "warship", "carrier", "carriage", "barge", "trap", "hunter", "animal", "animals", "swarm", "crowds", "revolt", "execute", "abdicate", "throne", "democracy", "dictator", "dictatorship", "aristocrat", "aristocracy", "merit", "meritocracy", "palace", "president", "evening", "enjoyable", "parachute", "ships", "port", "airfield", "airport", "support", "beam", "stack", "smoke", "pipe", "sweet", "sour", "bitter", "war", "battle", "cattle", "drink", "meat", "breed", "meet", "meeting", "north", "south", "east", "west", "valley", "prairy", "maid", "maiden", "voyage", "account", "accountant", "law", "lawyer", "politics", "politician", "political", "society", "map", "bank", "coin", "coins", "notes", "deposit", "banknote", "note", "shopkeeper", "owner", "lab", "laboratory", "machine", "generator", "bad", "good", "back", "pack", "chest", "drawer", "draw", "tie", "shirt", "shoes", "boot", "boots", "shoe", "battles", "wars", "hair", "hairs", "pasture", "father", "mother", "son", "daughter", "sons", "daughters", "fathers", "mothers", "grandmother", "grandfather", "grandparents", "parents", "door", "hear", "knock", "knocks", "heaven", "hell", "hospital", "chamber", "room", "doctor", "staff", "nurse", "ambulance", "heal", "care", "healthcare", "pirate", "step", "steps", "draws", "swords", "shield", "wooden", "wood", "frame", "mast", "oar", "boats", "wave", "waves", "treasure", "island", "land", "lands", "islands", "cannon", "ball", "balls", "heavy", "weight", "mass", "bodies", "dead", "alive", "hat", "patch", "eye", "detective", "investigate", "search", "dig", "loot", "family", "respected", "respect", "dive", "compass", "captain", "club", "dance", "dances", "shakes"]
fileNames: list[str] = []
latencyList: list[int] = []

def exportToCSV():
    #filename = f"clientLog_{requestRate}_{numRequests}.csv"
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               f"clientLog_{requestRate}_{numRequests}_Phase3.csv")
    with req_lock:
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["reqID", "keyword", "text", "response", "e2eTime_us"])
            for r in req:
                writer.writerow([r.reqID, r.keyword, r.text, r.response, r.e2eTime])

def rollingAverage() -> int:       #rolling average latency of the last X seconds of requests
    global latencyList
    summ = 0
    for latency in latencyList:
        summ+=latency
    return summ // max(len(latencyList),1)

def updateLL(newLatency:int):
    global latencyList
    if(len(latencyList)>=requestRate*rollingAveragePeriod):
        latencyList.pop(0)
    latencyList.append(newLatency)

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
        e2eTime=-1         #request creation time in μs
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
                    updateLL(r.e2eTime)
                    return r
        else:
            for r in reversed(req):
                if r.reqID == id:
                    r.response = resp
                    r.e2eTime = (time.time_ns() // 1000) - r.e2eTime
                    updateLL(r.e2eTime)
                    return r
    #no fail protection, not needed but should exist


def receiveResponse(
    async_result,
    done_sem: threading.Semaphore,
    conn,
    bg
):
    try:
        id, resp = async_result.value

        r = closeRequest(id, resp)

        print(
            f"id={r.reqID} "
            f"keyword={r.keyword} "
            f"text={r.text} "
            f"response={r.response} "
            f"latency={r.e2eTime / 1000:.2f}ms "
            f"RAL={rollingAverage() / 1000:.2f}ms"
        )

    finally:
        try:
            bg.stop()
        except Exception:
            pass

        try:
            conn.close()
        except Exception:
            pass

        done_sem.release()


def sendRequests(
    host: str,
    port: int,
    rate_hz: float,
    done_sem: threading.Semaphore,
    num_requests: int
):
    interval = 1.0 / rate_hz
    next_send = time.perf_counter()

    for i in range(num_requests):

        r = newRequest()

        # NEW RPyC/TCP connection for every request
        conn = rpyc.connect(host, port)

        bg = rpyc.BgServingThread(
            conn,
            serve_interval=0.1,
            sleep_interval=0
        )

        async_count = rpyc.async_(conn.root.count)

        # latency starts immediately before sending the RPC
        r.e2eTime = time.time_ns() // 1000

        async_result = async_count(
            r.reqID,
            r.keyword,
            r.text
        )

        async_result.add_callback(
            lambda ar,
                   s=done_sem,
                   c=conn,
                   b=bg:
            receiveResponse(ar, s, c, b)
        )

        print(f"Opened connection for request {r.reqID}")

        next_send += interval
        sleep_time = next_send - time.perf_counter()

        if sleep_time > 0:
            time.sleep(sleep_time)

def latencyStatsMs():
    with req_lock:
        completed = sorted(
            r.e2eTime for r in req
            if r.e2eTime >= 0
        )

    if not completed:
        return 0.0, 0.0

    # Average
    avg_ms = (sum(completed) / len(completed)) / 1000

    # 99th percentile - nearest-rank method
    p99_index = max(0, int(0.99 * len(completed) + 0.999999) - 1)
    p99_ms = completed[p99_index] / 1000

    return avg_ms, p99_ms

def main():

    random.seed(42)

    readAvailableFileNames()

    host = os.getenv(
        "SERVER_HOST",
        "loadbalancer"
    )

    port = int(
        os.getenv(
            "SERVER_PORT",
            "18861"
        )
    )

    done_sem = threading.Semaphore(0)

    print(
        f"Starting test: "
        f"{numRequests} requests @ {requestRate} req/s"
    )

    sendRequests(
        host,
        port,
        requestRate,
        done_sem,
        numRequests
    )

    # wait until every request has received a response
    for _ in range(numRequests):
        done_sem.acquire()

    avg_latency, p99_latency = latencyStatsMs()

    print(f"Average latency: {avg_latency:.2f} ms")
    print(f"P99 latency: {p99_latency:.2f} ms")

    print(f"Average latency: {avg_latency:.2f} ms")

    if exportLogs:
        exportToCSV()
        print("LOG FILE EXPORTED")

    print("CLIENT HAS FINISHED EXECUTING")


if __name__ == "__main__":
    main()