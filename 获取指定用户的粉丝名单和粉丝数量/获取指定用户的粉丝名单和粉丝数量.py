import requests
import json
#获取指定用户的粉丝名单和粉丝数量

#创建一个字典对象，用于构建请求头
headers={}

cookie = "SESSDATA=你的B站SESSDATA"
User_Agent = "Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.21.2"
vmid = 20893553
ps = 100
pn = 1

def buildHearders():
    headers["User-Agent"] = User_Agent

def main():
    buildHearders()
    Url = "http://api.bilibili.com/x/relation/followers"
    #构建请求体
    param = {"vmid": vmid,"ps":ps,"pn":pn}
    result = requests.request("GET", Url,headers=headers,params=param)
    r = json.loads(result.content)
    print("用户{}的粉丝数为{}".format(vmid,r["data"]["total"]))
    print("用户{}的粉丝名单如下：".format(vmid))
    for i in r["data"]["list"]:
        print(i["uname"])

if __name__ == "__main__":
    main() 