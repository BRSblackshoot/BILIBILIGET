import time
import requests
import json
import openpyxl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from tqdm import tqdm

#获取指定视频的所有评论并保存在excel中
#目标视频的BV号 格式诸如 BVxxxxxxx
oid = "BV1T4411f7MD"
#个人在B站的SESSDATA
cookie = "你的SESSDATA"
#爬虫从哪页开始爬取 非必要 默认为1
pn = 1
#评论区每一页显示数量 非必要 默认为20 范围1~49
ps = 49
#给定excel文件保存路径和名字
excel_path = "F:\游戏小工具\B站\\"
excel_name = "信息.xlsx"


############ av和bv互相转换 #####################
table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF' #码表
tr = {} #反查码表
#初始化反查码表
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6] #位置编码表
xor = 177451812 #固定异或值
add = 8728348608 #固定加法值

def bv2av(x):
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58 ** i
    return (r - add) ^ xor

def av2bv(x):
    x = (x ^ xor) + add
    r = list('BV1  4 1 7  ')
    for i in range(6):
        r[s[i]] = table[x // 58 ** i % 58]
    return ''. join(r)
###################################################

def buildHearders():
    #创建一个字典对象，用于构建请求头
    global headers
    headers={}
    User_Agent = "Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.21.2"
    headers["User-Agent"] = User_Agent

def buildNumber():
    global oid
    oid = bv2av(oid)

def buildExcel():
    # 创建一个Excel workbook 对象
    global sh,book
    book = openpyxl.Workbook()
    sh = book.active
    sh.title = '评论区'
    # 写标题栏
    sh['A1'] =  '评论者UID'
    sh['B1'] =  '评论者昵称'
    sh['C1'] =  '评论者性别'
    sh['D1'] =  '评论者签名'
    sh['E1'] =  '评论内容'
    sh['F1'] =  '根评论'

def buildRequest():
    Url = "http://api.bilibili.com/x/v2/reply"
    #构建请求体
    param = {"oid": oid,"type":1,"sort":2,"nohot":1,"pn":pn,"ps":ps}
    result = requests.request("GET", Url,headers=headers,params=param)
    return json.loads(result.content)

def buildRequestForReply(root,pn_R,ps_R):
    Url = "http://api.bilibili.com/x/v2/reply/reply"
    #构建请求体
    param = {"oid": oid,"type":1,"root":root,"pn":pn_R,"ps":ps_R}
    result = requests.request("GET", Url,headers=headers,params=param)
    return json.loads(result.content)

def buildRequestForTop():
    Url = "http://api.bilibili.com/x/v2/reply/main"
    #构建请求体
    param = {"oid": oid,"type":1}
    result = requests.request("GET", Url,headers=headers,params=param)
    return json.loads(result.content)

def strOp(str):
    #解决各种openpyxl写入时出现openpyxl.utils.exceptions.IllegalCharacterError错误，将openpyxl定义的非法字符用空字符代替
    return ILLEGAL_CHARACTERS_RE.sub(r'', str)

def getReply(rpid):
    #外层对一条评论的rcount进行判断，如果不等于0 那么就启用这个爬取获得回复区所有评论
    # 每次爬取 从回复区第一页开始
    pn_R = 1
    # 每页显示数量，默认20 定义域：1-49
    ps_R = 49
    while True:
        r=buildRequestForReply(root=rpid,pn_R=pn_R,ps_R=ps_R)
        #如果数据不为空 才执行后续操作
        if r["data"]["replies"] != None :
            #每当爬取了偶数页 休息2秒 降低爬虫被拦截的风险
            if pn_R%2 == 0:
                time.sleep(2)
            for i in r["data"]["replies"]:
                #该评论的发送者uid
                uid=i["mid"]
                #该评论的发送者的昵称
                nike=strOp(i["member"]["uname"])
                #该评论的发送者的性别
                sex=strOp(i["member"]["sex"])
                #该评论的发送者的签名
                sign = strOp(i["member"]["sign"])
                #该评论具体的发言
                message=strOp(i["content"]["message"])
                #该评论的根评论 如果本身就是根评论 则为0 根评论的回复区所有评论一律设为1
                root=i["root"]
                if root != 0:
                    root = 1

                #构建一个列表
                list_=(uid,nike,sex,sign,message,root)
                #将评论追加到excel末尾一行
                sh.append(list_)
        else:
            #终止循环
            break

        #执行完毕 开始请求下一页
        pn_R = pn_R + 1

def getTop():
    r=buildRequestForTop()
    #如果数据不为空 才执行后续操作
    if len(r["data"]["top_replies"]) != None:
        for i in r["data"]["top_replies"]:
            #该评论的发送者uid
            uid=i["mid"]
            #该评论的发送者的昵称
            nike=strOp(i["member"]["uname"])
            #该评论的发送者的性别
            sex=strOp(i["member"]["sex"])
            #该评论的发送者的签名
            sign = strOp(i["member"]["sign"])
            #该评论具体的发言
            message=strOp(i["content"]["message"])
            #该评论的根评论 如果本身就是根评论 则为0 根评论的回复区所有评论一律设为1
            root=i["root"]
            if root != 0:
                root = 1

            #构建一个列表
            list_=(uid,nike,sex,sign,message,root)
            #将评论追加到excel末尾一行
            sh.append(list_)

            #下面针对单个评论 判断是否有回复区 如果有 读取保存
            if i["rcount"] != 0:
                getReply(i["rpid"])

def main():
    buildHearders()
    buildNumber()
    buildExcel()
    # 一般爬虫被拦截时会导致IF判断报错 此时可以捕捉类型异常 保存已经爬取到的数据
    try:
        getTop()
        while True:
            r=buildRequest()
            #如果数据不为空 才执行后续操作
            if len(r["data"]["replies"]) != 0:
                global pn
                print("开始爬取第{}页数据".format(pn))
                for i in tqdm(r["data"]["replies"]):
                    #该评论的发送者uid
                    uid=i["mid"]
                    #该评论的发送者的昵称
                    nike=strOp(i["member"]["uname"])
                    #该评论的发送者的性别
                    sex=strOp(i["member"]["sex"])
                    #该评论的发送者的签名
                    sign = strOp(i["member"]["sign"])
                    #该评论具体的发言
                    message=strOp(i["content"]["message"])
                    #该评论的根评论 如果本身就是根评论 则为0 根评论的回复区所有评论一律设为1
                    root=i["root"]
                    if root != 0:
                        root = 1

                    #构建一个列表
                    list_=(uid,nike,sex,sign,message,root)
                    #将评论追加到excel末尾一行
                    sh.append(list_)

                    #下面针对单个评论 判断是否有回复区 如果有 读取保存
                    if i["rcount"] != 0:
                        getReply(i["rpid"])

            else:
                #终止循环
                break

            #执行完毕 开始请求下一页 
            pn = pn + 1
            #每当爬取了偶数页 休息2秒 降低爬虫被拦截的风险
            if pn%2 == 0:
                time.sleep(2)
            

        #数据都保存到excel对象中 excel对象保存在内存中 现在需要将其保存到硬盘上
        book.save(excel_path+excel_name)
        #完成
        print("爬虫爬取完成")
    except TypeError:
        book.save(excel_path+excel_name)
        print("遭遇异常，爬虫停止，爬取过的数据已经保存")

if __name__ == "__main__":
    main() 