from os import error
from bs4 import BeautifulSoup
import requests
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import subprocess as sp
from slugify import slugify
import os.path
import time
import json

Key = "AIzaSyDiuoh9uRKaRc19MGmg_S9whZM6h68W6No"
BlogId = "7132956052456559285"
blogId_main = "7886686801878753136"
SCOPES = [  'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/blogger',
            "https://www.googleapis.com/auth/drive.file",
            'https://www.googleapis.com/auth/drive.appdata',
            
]

def getTruyenNgonTinh(url):
    full_page = requests.get(url)
    element = BeautifulSoup(full_page.text,'html.parser')
    title = element.find("h1").text
    author = element.find("a","author").text
    status = element.find("div","mt-status").text.replace("\nTrạng thái: ","").strip()
    if status == "Full":
        status = "FULL"
    else:
        status = "Updating"
    labels1 = ["Tác giả " + author,status,"Ngôn tình"]
    description = element.find("div","summary-content")
    p = element.find("div","summary-content")  
    for i in p.find_all("a"):
        i.decompose()
    p  = BeautifulSoup(str(p),'html.parser')
    p.div.unwrap()

    link = element.find("div","manga-thumb").find("img")['src']
    image = upload_img(link,title)
    sheetid = tao_sheet()
    body = {
        "title" : title,
        "titleLink" : "https://www.truyencf.cf/" + sheetid,
        "labels" : labels1,
        "content" : str(p) + "<img src='"+ image +"'>"

    }
    
    dang_truyen = blog.posts().insert(blogId=blogId_main, body=body).execute()
    return dang_truyen

def getTruyenFull(_url):
    _req = requests.get(_url)
    _content = BeautifulSoup(_req.content,'html.parser')
    #Lay noi dung truyen
    _title = _content.find(class_="title").text
    _info =  _content.find(class_="info").find_all("div")
    _author  = _info[0].text.replace(":"," ")
    list_label = [i.text for i in _info[1].find_all("a") ]
    _status =  _info[3].find("span").text
    p = _content.find("div","desc-text")  
    for i in p.find_all("a"):
        i.decompose()
    p  = BeautifulSoup(str(p),'html.parser')
    p.div.unwrap()
    if _status == "Full":
        _status = "FULL"
    else:
        _status = "Updating"
    _link_image = _content.find(class_="book").find("img").get("src")
    labels1 = [_author,_status]
    labels1.extend(list_label)
    _image = upload_img(_link_image,_title)

    #Tao Sheet
    _sheetid = tao_sheet(_title)
    #Lay trang
    pages = _content.find(class_="pagination")    
    if ( pages ):
        pages = pages.find_all("a")
        last_page = pages[len(pages) -2].get("href").split("/")
        last_page = int( last_page[len(last_page) - 2].split("-")[1])
    else:
        last_page = 1
    #Lay chapter
    list = []
    for page in range(1,last_page+1):
        url = _url + "trang-" + str(page)
        print(url)
        req = requests.get(url)
        content = BeautifulSoup(req.content,'html.parser')   
        a = content.find(class_="list-chapter")
        b = a.find_all("a")
        for link in b:
            list.append(link.get("href"))
    #Updata Sheets
    for i in list:
        _list = get_truyenfull(i)
        print(len(_list[2]))
        if(len(_list[2]) >= 50000 ) :
            print("Chua them :" + i)
        else:
            value_range_body["values"].append(_list)
            print("da them : " + i)
    request = service.spreadsheets().values().append(spreadsheetId=_sheetid, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
    #Đăng bài
    body = {
        "title" : _title,
        "titleLink" : "https://www.truyencf.cf/" + _sheetid,
        "labels" : labels1,
        "content" : str(p) + "<img src='"+ _image +"'>"

    }
    
    dang_truyen = blog.posts().insert(blogId=blogId_main, body=body).execute()
    return dang_truyen
def getList():
    list = []
    with open("file.txt","r") as file:
        while(True):
            line = file.readline()
            if not line:
                break
            list.append(line.rstrip("\n"))
        file.close()
    return list

def get_chapter(url):
    full_page = requests.get(url)
    element = BeautifulSoup(full_page.text,'html.parser')
    title = element.find_all("div","manga-chapter-head")
    content = element.find_all("div","box-chapter-content")
    content = str(content[0])
    content = content[33:(len(content)-6)]
    label = element.find_all("div","manga-chapter-head")[0].find("h1").text
    chapter_title = element.find_all("div","manga-chapter-head")[0].find("h2").text.strip()
    chapter_title = " ".join(chapter_title.split()) 
    number = chapter_title.split(":")
    if(len(number)==1):
        list=[number[0],"",content]
    else:
        list = [number[0],number[1],content]
    return  list

def get_truyenfull(url):
    full_page = requests.get(url)
    element = BeautifulSoup(full_page.text,'html.parser')
    content = element.find_all("div","chapter-c")[0]
    for div in content.find_all("div", {'class':'visible-md'}): 
        div.decompose()
    content = str(content)
    content = content[38:(len(content)-6)]
    #label = element.find_all("div","manga-chapter-head")[0].find("h1").text
    chapter_title = str( element.find_all("div","col-xs-12")[0].find("h2").text.strip() )
    chapter_title = " ".join(chapter_title.split()) 
    number = chapter_title.split(":")
    if(len(number)==1):
        list=[number[0],"",content]
    else:
        list = [number[0],number[1],content]
    return  list

def getTruyenTr(url):
    full_page = requests.get(url)
    element = BeautifulSoup(full_page.text,'html.parser')
    content = element.find_all("div","chapter-c")[0]
    for div in content.find_all("div"): 
        div.decompose()
    for div in content.find_all("script"): 
        div.decompose()
    content = str(content)
    content = content[42:(len(content)-6)]
    #label = element.find_all("div","manga-chapter-head")[0].find("h1").text
    chapter_title = str( element.find_all("div","rv-chapt-title")[0].find("h2").text.strip() )
    chapter_title = " ".join(chapter_title.split()) 
    number = chapter_title.split(":")
    if(len(number)==1):
        list=[number[0],"",content]
    else:
        list = [number[0],number[1],content]
    return  list
    

def update_truyen(id_post,titleLink):
    update_p = {"titleLink":titleLink}
    update_post = blog.posts().patch(blogId=blogId_main, postId=id_post,body=update_p).execute()

def publish_truyen(id_post):
    publist_truyen = blog.posts().publish(blogId=blogId_main, postId=id_post).execute()

def tao_sheet(k=''):
    if (k==''):
        name = input("Nhap ten truyen : ")
    else:
        name = k
    data = {
            "driveId" : "1zEDhCj8Pniu-47LqUP_v8pku-qAQqrsd",
            "name" : name, 
    }
    drive_request = drive.files().copy(fileId="1PJReQf63DMdrPGYeHT3umP2D1rBNu07wSQMv-dyTu2Y",body=data)
    drive_response = drive_request.execute()
    #print(drive_response)
    sheetid = drive_response['id']
    return sheetid


def upload_img(url,title):
    f = open('token2.json',"r")
    data = json.load(f)        
    f.close()
    print(data['token'])
    headers = {"Authorization": "Bearer " + data['token']}
    para = {
            "title": title+".jpg",
            "parents": [{"id": "1kUBhVSxQUyfjXFmEupC2laDKW8oLbMVX"}]
    }
    files = {
            "data": ("metadata", json.dumps(para), "application/json; charset=UTF-8"),
            "file": requests.get(url).content
    }
    response = requests.post("https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart", headers=headers, files=files)
    response = response.json()
    link = response['thumbnailLink'].replace("=s220","")
    print(link)
    return link


def upload(service, file):
    f = requests.get(file).content
    fa = open('token2.json',"r")
    data = json.load(fa)        
    fa.close()

    url = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {
            'Authorization': "Bearer " + data['token'],
            'Content-Type': 'application/octet-stream',
            'X-Goog-Upload-File-Name': file,
            'X-Goog-Upload-Protocol': "raw",
    }

    r = requests.post(url, data=f, headers=headers)
    print ('\nUpload token: %s' % r.content)
    return r.content.decode()

def createItem(service, upload_token, albumId):
    fa = open('token2.json',"r")
    data = json.load(fa)        
    fa.close()
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'

    body = {
        'newMediaItems' : [
                {
                    "description": "test upload",
                    "simpleMediaItem": {
                        "uploadToken": upload_token,
                    }  
                }
            ]
        }

    if albumId is not None:
        body['albumId'] = albumId
    bodySerialized = json.dumps(body)
    print(bodySerialized)
    headers = {
            'Authorization': "Bearer " + data['token'],
            'Content-Type': 'application/json',
    }

    r = requests.post(url, data=bodySerialized, headers=headers)
    print ('\nCreate item response: %s' % r.content)
    return r.content

# authenticate user and build service



id_post = None
status = None
sheetid = None
name_post = None
while True:
    creds = None
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)

    if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token2.json', 'w') as token:
                token.write(creds.to_json())

    range_ = 'Sheet1!A:C' 
    value_input_option = 'USER_ENTERED'  
    insert_data_option = 'OVERWRITE'  
    value_range_body = {
                "values":[
                ]
    }
    #print(creds)

    service = build('sheets', 'v4', credentials=creds)
    blog = build('blogger','v3',developerKey=Key,credentials=creds)
    drive = build('drive', 'v3', credentials=creds)
    photo = build('photoslibrary', 'v1', credentials=creds,static_discovery=False)
    sp.call('cls', shell=True)
    print("******"+ str(name_post) + "***********************************" )
    print("******ID : " + str(id_post) +"(" +str(status) + ")*************** ")
    print("******Sheet ID : "+ str(sheetid) +" *********************")
    print("1. Chọn truyện ")
    print("2. Tạo danh sách truyện ")
    print("3. Them chapter cho truyen")
    print("4. Get truyện (Chỉ dùng cho truyện chưa được đăng)")
    print("e. Upload ảnh")
    print("0. Thoat")
    select = input("Bạn chọn : ")
    if(select=='1'):
        a = input("Chon truyen : (1- ID) (2-Search) (3- Draft)")
        if(a=='1'):
            id_post = input("Vui lòng nhập id truyện : ")
        elif(a=='2'):
            search_key = input("Vui lòng nhập tên truyện : ")
            posta = blog.posts().search(blogId = blogId_main,q=search_key).execute()
            data = {'title':[] , 'id' :[], 'sheetid' :[] }
            len_post = range( len(posta["items"]) )
            for i in len_post:
                data['title'].append(posta["items"][i]["title"])
                data['id'].append(posta["items"][i]["id"])
                try:
                    data['sheetid'].append(posta["items"][i]["titleLink"].split("/")[3])
                except:
                    data['sheetid'].append(None)
            print("Vui lòng chọn truyện : ")
            for i in data['title']:
                print(str(data['title'].index(i)) +". "+str(i))
            k = int(input("Ban chon : "))
            id_post =data['id'][k]
            status = "LIVE"
            try:
                sheetid=data['sheetid'][k]
            except:
                pass
        elif(a=='3'):
            posta = blog.posts().list(blogId = blogId_main,status='DRAFT').execute()
            data = {'title':[] , 'id' :[],'status' : [] }
            len_post = range( len(posta["items"]) )
            for i in len_post:
                data['title'].append(posta["items"][i]["title"])
                data['id'].append(posta["items"][i]["id"])
                data['status'].append(posta["items"][i]["status"])
            print("Vui lòng chọn truyện : ")
            for i in data['title']:
                print(str(data['title'].index(i)) +". "+str(i))
            k = int(input("Ban chon : "))
            id_post =data['id'][k]
            status = data['status'][k]
    elif(select=='2'):
        sheetid = tao_sheet()
        update_truyen(id_post,"https://www.truyencf.cf/"+sheetid)
    elif(select=='3'):
        urls = getList()
        c = input("Chon nguon : (1 - Webngontinh ) ( 2 - TruyenFull ) (3 - TruyenTr): ")
        if ( c == '1' ):   
            for i in urls:
                list = get_chapter(i)
                print(len(list[2]))
                if(len(list[2]) >= 50000 ) :
                    print("Chua them :" + i)
                else:
                    value_range_body["values"].append(list)
                    print("da them : " + i)
        elif ( c == '2' ):
            for i in urls:
                list = get_truyenfull(i)
                print(len(list[2]))
                if(len(list[2]) >= 50000 ) :
                    print("Chua them :" + i)
                else:
                    value_range_body["values"].append(list)
                    print("da them : " + i)
        elif (c == '3'):
            for i in urls:
                list = getTruyenTr(i)
                print(len(list[2]))
                if(len(list[2]) >= 50000 ) :
                    print("Chua them :" + i)
                else:
                    value_range_body["values"].append(list)
                    print("da them : " + i)
        request = service.spreadsheets().values().append(spreadsheetId=sheetid, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
        response = request.execute()
    elif(select == '4'):
        _select = input("Chon web (1.WebNgonTinh) (2.TruyenFull) : ")
        if(_select == '1'):
            url = input("Nhap url truyen : ")
            re = getTruyenNgonTinh(url)
            print(re)
        elif(_select == '2'):
            url = input("Nhap link truyen : ")
            re = getTruyenFull(url)
    elif(select == 'e'):
        f = open('token2.json',)
        data = json.load(f)        
        f.close()
        headers = {"Authorization": "Bearer " + data['token'],}
        para = {
            "title": "abssc.jpg",
            "parents": [{"id": "1kUBhVSxQUyfjXFmEupC2laDKW8oLbMVX"}]
        }
        files = {
            "data": ("metadata", json.dumps(para), "application/json; charset=UTF-8"),
            "file": requests.get("https://media.webngontinh.com/images/w180/2019/09/30/choc-tuc-vo-yeu-mua-mot-tang-mot.jpg").content
        }
        response = requests.post("https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart", headers=headers, files=files)
        response = response.json()
        print(response)
        print (response['thumbnailLink'])
        break        
    elif(select== 'f'):
        upload_token = upload(photo, 'https://img.8cache.com/hot-2.jpg')
        response = createItem(photo,upload_token,"AIM4SgBal7WfGY3lXe5rrg1G1VUVwoOGtF1txs3XGnbXaNbEbyAUTBtGqom8w1Gtj1bodjr16zCk")
    elif(select =='g'):
        f = open('token2.json',)
        data = json.load(f)        
        f.close()
        headers = {
            "Authorization": "Bearer " + data['token'],
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        body = {"album":{"title":"WebTruyenBlogger"}}
       
        response = requests.post("https://photoslibrary.googleapis.com/v1/albums?key="+Key, headers=headers, data=json.dumps(body))
        response = response.json()
        print(response)
        

    else:
        break   
    sp.call('pause', shell=True)
 
  
print("exit")

'''
l =getTruyenTr("https://truyentr.org/truyen/xuyen-viet-lam-vo-nguoi-ta/chuong-1/")
print(l[1])
'''