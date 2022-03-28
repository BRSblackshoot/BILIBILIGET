import requests
import json
import time
#定时获取指定视频的播放量

#创建一个字典对象，用于构建请求头
headers={}

cookie = "SESSDATA=你的SESSDATA"
User_Agent = "Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.21.2"
bvid = "目标视频的BV号"

def buildHearders():
    headers["User-Agent"] = User_Agent

def main():
    buildHearders()
    Url = "http://api.bilibili.com/x/web-interface/view"
    #构建请求体
    param = {"bvid": bvid}
    result = requests.request("GET", Url,headers=headers,params=param)
    r = json.loads(result.content)
    print(r["data"]["stat"]["view"])

if __name__ == "__main__":
    main()#第一次执行
    # 用死循环实现定时任务
    while True:
        #睡眠一小时
        time.sleep(3600)
        #获取播放量
        main()