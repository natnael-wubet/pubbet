import sys
import os
import time
from socket import *


sock = socket(2,1)
sock.bind(('0.0.0.0',8080))
sock.listen(10)
token = {
    "s":"dalkfweqfwe",
    "sent":0,
    "pass":"p123wd"
}
data = {
    "beters":{
        "0918282818": {
            "1": {
                "cat":"sport",
                "id":"1",
                "choise":"0",
                "payed":"0"
            }
        }
    },
    "news":{
        "sport":{
            "1":{

                "title":"liv vs man",
                "detail":"the final game",
                "id":"0",
                "active":"1",
                "date":"11/11/11",
                "price":"5",
                "choise":"man,liv",
                "bets":"10,10",
                "beters":""
            },
            "2":{

                "title":"Arsenal vs Manchister",
                "detail":"the final game",
                "id":"0",
                "active":"1",
                "date":"11/11/11",
                "price":"100",
                "choise":"man,liv,Draw",
                "bets":"6000,4000,5000",
                "beters":""
            }
        },
        "politics":{
            "1":{

                "title":"election 2020",
                "detail":"bet for your best",
                "id":"0",
                "active":"1",
                "date":"11/11/11",
                "price":"25",
                "choise":"mr x,dr b,ps s",
                "bets":"5000,4500,5551",
                "beters":""
            }
            
        },
        "entertiment": {
            "1":{

                "title":"award  ",
                "detail":"the final game",
                "id":"0",
                "active":"1",
                "date":"11/11/11",
                "price":"5",
                "choise":"man,liv",
                "bets":"300,400",
                "beters":""
            }
        }
        
    }
}

def response(txt):
    ret = '''HTTP/1.1 200 OK
Transfer-Encoding: text/html
Server: Microsoft-HTTPAPI/2.0
Date: %s

'''%(time.asctime(time.localtime(time.time())))
    ret = ret.replace("\n","\r\n")
    return ret+txt
def to_jsonObj(obj):
    ret = "{"
    c=0
    for i in obj:
        if c!=0:
            ret+=","
        
        if type(obj[i]) == int:
            ret += "\n\t'%s' = %s"%(i,obj[i])
        elif type(obj[i]) == dict:
            ret+= "\n\t'%s' = '%s'"%(i,to_jsonObj(obj[i]))
        else:
            ret += "\n\t'%s' = '%s'"%(i,obj[i])
        c+=1
    ret += "\n\t}"
    return ret
def from_jsonObj(obj):
    ret = {}
    objs = obj.split("\n\t")
    for i in range(len(objs)):
        if (len(objs[i].split("=")) >1 ):
            if objs[i].split("=")[1][1] == "'":
                ret.update({"%s"%objs[i].split("=")[0]:"%s"%objs[i].split("=")[1]})
            else:
                ret.update({"%s"%objs[i].split("=")[0]:int("%s"%objs[i].split("=")[1])})
    return ret
def to_jsonArray(obj):
    ret = "["
    for i in obj:
        ret += "\n%s,"%(to_jsonObj(obj[i]))
    ret += "\n]"
    return ret
def get_beters():
    ret = ""
    c=0
    for i in data["beters"]:
        for j in data["beters"][i]:
            me = data["beters"][i][j]
            if me["payed"]=="0":
                c+=1
                game = data["news"][me["cat"]][me["id"]]
            
                ret += "%i) phone:[ %s ] game:[ %s ] choosed:[ %s ] price:[ %s ]\n"%(c,i,game["title"], game["choise"].split(',')[int(me["choise"])], game["price"])
    return ret

def join(x,y):
    ret = ""
    for i in x: ret+=i+y
    return ret
def approve_beter(x):
    ret = ""
    c=0
    for i in data["beters"]:
        for j in data["beters"][i]: 
            me = data["beters"][i][j]
            
            if me["payed"]=="0":
                c+=1

                if c==int(x):
                    data["beters"][i][j]["payed"]="1"
                    ch = data["news"][me["cat"]][me["id"]]["bets"].split(",")
                    ch[int(me["choise"])] = "%s"%(int(ch[int(me["choise"])])+1)
                    data["news"][me["cat"]][me["id"]]["bets"] = join(ch,",")
                    data["news"][me["cat"]][me["id"]]["beters"]+="%s,"%i
                    return 
def can_bet(phone,cat,id):
    x = data["news"][cat][id]["beters"].split(",")
    print (not phone in x),data["news"][cat][id]
    return not phone in x
while 1:
    con,addr = sock.accept()
    rec = con.recv(1024).split(" ")
    if rec[0] == "admin":
        if rec[1] == "token" and rec[2]==token["pass"]:
            
            con.sendall(token["s"])
            token["sent"]=1
        elif rec[1] == "news":
            if len(rec)>=7:
                obj = {
                    "title":rec[3].replace("+"," "),
                    "detail":rec[4].replace("+"," "),
                    "id":"",
                    "active":"1",
                    "date":rec[5].replace("+"," "),
                    "price":rec[6],
                    "choise":rec[7].replace("+"," "),
                    "bets":"",
                    "beters":""
                }
                #print rec,obj
                obj["id"] = "%s"%(len(data["news"][rec[2]])+1)
                obj["bets"] = "0"
                obj["bets"] += ",0"*(len(obj["choise"].split(","))-1)
                data["news"][rec[2]].update({obj["id"]:obj})
        else:
            if rec[1] == token["s"]:
                if rec[2][0] == "a":
                    approve_beter(rec[2][1])
            con.sendall(get_beters())
    else:
        
        url = ("%s/////"%rec[1]).split("/")
        if url[1] == "news":
            if url[2] == "sport":
                ##print url,response(to_jsonArray(data["news"]["sport"]))
                con.sendall(response(to_jsonArray(data["news"]["sport"])))
            elif url[2] == "politic":
                con.sendall(response(to_jsonArray(data["news"]["politics"])))
            elif url[2] == "entert":
                con.sendall(response(to_jsonArray(data["news"]["entertiment"])))
        if url[1] == "bet":
            
            inp = url[3].split("_")
            cat = ("sport","politics","entertiment")
            
            if can_bet(inp[0],cat[int(inp[1])],"%s"%(int(inp[2])+1)):
                
                ##print inp
                obj = {
                    "cat":cat[int(inp[1])],
                    "id": "%s"%(int(inp[2])+1),
                    "choise": inp[3],
                    "payed": "0"
                }
                if inp[0] in data["beters"]:
                    data["beters"][inp[0]].update({"%s"%(len(data["beters"][inp[0]])+1):obj})
                else:
                    data["beters"].update({ inp[0]:{"1":obj} })
                ##print data["beters"]
                data["news"][cat[int(inp[1])]]["%s"%(int(inp[2])+1)]["beters"]+=inp[0]+","
            con.sendall(response(to_jsonObj({"1":"1"})))
    #print to_jsonArray(data["news"])
    ##print rec
    try:
        con.stop()
    except:
        pass
    con.close()
try:
    sock.stop()
except:
    pass

sock.close()
