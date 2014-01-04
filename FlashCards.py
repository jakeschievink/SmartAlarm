from httplib2 import Http
import json, random

class FlashCardGrabber():
    def __init__(self):
        self.http = Http()
        self.client_id = "gJ36CfTUxP"
    def getSet(self, cid):
        print "fetching cards"
        resp, content = self.http.request("https://api.quizlet.com/2.0/sets/"+str(cid)+"?client_id="+self.client_id)
        return json.loads(content)
    def searchSets(self, term):
        print "fetching search"
        resp, content = self.http.request("https://api.quizlet.com/2.0/search/sets?client_id="+self.client_id+"&q="+term+"&whitespace=1")
        print "response: ", resp, "content: ", content
        return json.loads(content)
    def saveSet(self, cid):
        rSet = self.getSet(cid)
        title = rSet["title"]
        with open("./sets/"+title+".json", 'w') as outfile:
            json.dump(rSet, outfile)

class FlashParser():
    def __init__(self, ffile):
        with open("./sets/"+ffile, 'r') as inputfile:
            self.f = json.load(inputfile)
    def parseFlash(self):
        return [(i["definition"], i["term"]) for i in self.f["terms"]]
    def getChoice(self):
        return random.choice(self.parseFlash())


    


