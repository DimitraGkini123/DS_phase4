import os
import rpyc
import time
import random

from dataclasses import dataclass

class request:
    reqID: int
    keyword: str
    text: str
    response: int
    e2eTime: int


req: list[request] = []
currID = 0

words: list[str] = ["sheep", "cow", "now", "then", "the", "end", "out", "eagle", "Monday", "geometry", "find", "crowd", "and", "time", "place", "go", "just", "minutes", "hours", "plug", "victory", "enemy", "friend", "ally", "we", "straight", "corner", "run", "attempt", "defeat", "failure", "welcome", "lap", "music", "goodbye", "come", "leave", "my", "your", "you", "he", "she", "puts", "takes", "gives", "look", "see", "visit", "need", "weekend", "gone", "option", "moment", "band", "stage", "glove", "stone", "power", "energy", "someone", "seconds", "first", "second", "man", "woman", "red", "black", "blue", "white", "green", "yellow", "white", "purple", "brown", "dark", "light", "orange", "tree", "plant", "flower", "read", "reality", "walk", "drive", "car", "plane", "bike", "bicycle", "bus", "taxi", "helicopter", "boat", "ship", "vehicle", "transport", "move", "engage", "miss", "hit", "sing", "song"]
fileNames: list[str] = []

def newRequest():
    
    req.append(request(
        reqID=currID,
        keyword=random.choice(words),                  #random word
        text=random.choice(fileNames),                 #from random text that is in the folder
        response = -1,
        e2eTime = time.time_ns() // 1000        #time in μs
        
    ))

    currID=currID+1

def closeRequest(id:int, resp:int):
    for r in req:
        if r.reqID == id:
            r.response = resp
            r.e2eTime = (time.time_ns() // 1000) - r.e2eTime
            

def readAvailableFileNames():
    fileNames = os.listdir("SampleTexts")
    fileNames = [name[:-4] for name in fileNames]
    #print(fileNames)

def main():
    readAvailableFileNames()
    #initializes rpyc connection to server1 on port 18861
    #conn = rpyc.connect("server1", 18861)

if __name__ == "__main__":
    main()


#calls function count on the server with arguments 
#result = conn.root.count("keyword", "file.txt")

#closes the connection
#conn.close()