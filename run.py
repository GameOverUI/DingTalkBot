#python 3.8 
import time,hmac,hashlib,base64,urllib.parse,sys,requests,json
from function import *
from lxml import etree
def sent_message(token:str,secret:str,text:str,title:str,picUrl:str,messageUrl:str):
    timestamp = str(round(time.time() * 1000))  
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    print(timestamp)
    print(sign)
    url="https://oapi.dingtalk.com/robot/send?access_token={2}&timestamp={0}&sign={1}".format(timestamp,sign,token)
    data={
        "msgtype": "link", 
        "link": {
            "text": text, 
            "title": title, 
            "picUrl": picUrl, 
            "messageUrl": messageUrl
        }
    }
    headers={"Content-Type": "application/json"}
    data=json.dumps(data)
    rsp=requests.post(url=url,data=data,headers=headers)
    print(rsp.json().get('errmsg'))




if __name__ == "__main__":
    
    token=sys.argv[1]
    secret = sys.argv[2]
    try:
        mids = sys.argv[3]
        bili_subscribe = True
    except:
        bili_subscribe =  False
    nowtime=time.time()
    #小刀网线报处理
    datas=get_message()      
    for url,img,info in datas:
        rsp=requests.get(url=url)
        s=etree.HTML(rsp.text)
        title=s.xpath("//h1[@class='article-title']")[0].text
        date=s.xpath("//time")[0].xpath('string(.)')        
        timeArray = time.strptime(date+":00", "%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(timeArray)
        ac_time=nowtime-timestamp+28800
        #默认时间频率为两小时，单位秒即7200，可以根据自己需求更改。中国为东八区，比标准时间快8小时。
        if ac_time<7200 :
            sent_message(token=token,secret=secret,text=date+"\n"+info,title=title,picUrl=img,messageUrl=url)
            print("log:",date,title,info,"\n")
        else:
            break
    #bilibili投稿处理
    if bili_subscribe == True :
        mid_list = mids.split(',')
        for i in mid_list:
            video_list = get_video(i)
            for j in video_list:
                ac_time = int(nowtime) - j['created'] +28800
                if ac_time<7200 :
                    sent_message(token=token,secret=secret,text=j['author']+"\n"+j['description'],title=j['title'],picUrl="https:{}".format(j['pic']),messageUrl="https://www.bilibili.com/video/{}".format(j['bvid']))
                    print("log:",j['created'],j['author'],j['title'],"\n")
                else:
                    break
    else:
        pass

        
    
    

