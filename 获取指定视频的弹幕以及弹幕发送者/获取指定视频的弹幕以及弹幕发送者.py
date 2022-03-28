import requests
import google.protobuf.text_format as text_format
import dm_pb2 as Danmaku
import openpyxl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from datetime import datetime
import midhash2uid

#获取指定视频的弹幕以及弹幕发送者并保存到excel中

#目标视频的cid
cid = 516508940
#弹幕分包 默认从1开始 基本不用动
segment_index = 1
#给定excel文件保存路径和名字
excel_path = "F:\\游戏小工具\\B站\\"
excel_name = "信息.xlsx"

def buildReq():
    url = 'http://api.bilibili.com/x/v2/dm/web/seg.so'
    params = {
        'type':1,  
        'oid':cid,
        'segment_index':segment_index
    }
    resp = requests.get(url,params)
    return resp.content

def buildExcel():
    # 创建一个Excel workbook 对象
    global sh,book
    book = openpyxl.Workbook()
    sh = book.active
    sh.title = '弹幕信息'
    # 写标题栏
    sh['A1'] =  '发送者UID'
    sh['B1'] =  '弹幕内容'
    sh['C1'] =  '弹幕发送时间'
    sh['D1'] =  '视频内弹幕出现时间'

def strOp(str):
    #传入的格式为'content: "← 雪山顶端圣遗物本里"' 需要从中取出实际弹幕内容
    str = str.lstrip('content: "')
    str = str.rstrip('"')
    #解决各种openpyxl写入时出现openpyxl.utils.exceptions.IllegalCharacterError错误，将openpyxl定义的非法字符用空字符代替
    return ILLEGAL_CHARACTERS_RE.sub(r'', str)

def timeOp(t):
    #将timestamp转换为datetime 注意传入的t格式为'ctime: 1611650233' 并不是数字格式 需要处理
    t = t.lstrip('ctime: ')
    t = int(t)
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")

def UID(midhash):
    #传入的格式为'midHash: "b0c7f2f7"' 需要从中取出b0c7f2f7
    midhash = midhash.lstrip('midHash: "')
    midhash = midhash.rstrip('"')
    #反查出uid 后续使用发现反查花费的时间太久了 这个反查功能还是跳过吧 没必要所有弹幕都去查 只在遇到感兴趣的弹幕时再去专门反查比较合适
    # return midhash2uid.getUid(midhash)
    return midhash

def sTimeOp(millis):
    #传入的格式为'progress: 169029' 需要从中取出169029
    millis = millis.lstrip('progress: ')
    #毫秒转秒 取整数
    seconds = int(millis)/1000
    #python divmod() 函数把除数和余数运算结果结合起来，返回一个包含商和余数的元组(a // b, a % b)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d"%(h, m, s)

def msg2excel(data):
    #逐一读取弹幕信息
    for i in data.elems:
        #初始化变量
        show_t ="字段缺失"
        uid = "字段缺失"
        dm = "字段缺失"
        t = "字段缺失"

        #解析弹幕信息
        msg = text_format.MessageToString(i,as_utf8=True)
        #将str切分为list
        msg = msg.split("\n")
        for j in msg:
            #利用切片器加判断 找到需要的字段信息
            if j[:2] == "pr":
                #获取视频内弹幕出现时间
                show_t = j
                #将毫秒转为时分秒
                show_t = sTimeOp(show_t)
            if j[:2] == "mi":
                #获取加密过的mid字段
                midhash = j
                uid = UID(midhash)
            if j[:2] == "co": 
                #获取弹幕内容
                dm = j
                #解决弹幕内容存在的非法字符问题
                dm = strOp(dm)
            if j[:2] == "ct":
                #获取弹幕发送时间
                t = j
                #解决时间戳问题
                t = timeOp(t)

        #保存数据到excel
        list_=(uid,dm,t,show_t)
        sh.append(list_)

def main():
    buildExcel()
    midhash2uid.create_table()
    while True:
        data = buildReq()
        #如果数据不为空 才执行后续操作
        if data != b'':
            #实例化对象
            danmaku_seg = Danmaku.DmSegMobileReply()
            #传入数据包
            danmaku_seg.ParseFromString(data)
            #数据处理
            msg2excel(danmaku_seg)
            #开始爬取下一个分包的数据
            global segment_index
            print("分包{}爬取完毕".format(segment_index))
            segment_index = segment_index + 1
            
        else:
            break
    
    #数据都保存到excel对象中 excel对象保存在内存中 现在需要将其保存到硬盘上
    book.save(excel_path+excel_name)
    print("弹幕爬取完毕")

if __name__ == "__main__":
    main() 