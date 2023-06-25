import discord
from discord.ext import commands
import requests, time, re
from bs4 import BeautifulSoup
import unicodedata
from urllib.parse import urlencode, urlparse, parse_qs, parse_qsl, unquote_plus
import asyncio
import feedparser
import pyshorteners
from datetime import datetime

def log(strinags):
    print("["+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"] [LOG      ] "+str(strinags))

## 게시글 제목과 리플 수를 파싱하여 리플 수가 일정 이상인 경우만 추출하는 함수 ##
def parse_hansicgu():
    log("scaning hansicgu")
    headers = { # 헤더를 넣지 않아도 작동하는 것을 확인했습니다.
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
   
    params = {
        'search.clubid' : '16259867', # 카페 ID
        'search.menuid' : '8', # 메뉴 ID
        'search.boardtype' : 'W', # 보드타입 (반드시 필요로 하는 것은 아닌 것 같습니다.)
        #'search.page' : page # 불러올 페이지
    }

    params2 = {
        'search.clubid' : '16259867', # 카페 ID
        'search.menuid' : '22', # 메뉴 ID
        'search.boardtype' : 'W', # 보드타입 (반드시 필요로 하는 것은 아닌 것 같습니다.)
        #'search.page' : page # 불러올 페이지
    }

    result_title = []
    result_url = []
    result_image = []
    url = 'https://cafe.naver.com/ArticleList.nhn'

    html = requests.get(url, headers = headers, params = params)
    soup = BeautifulSoup(html.text, 'html.parser')
    titles_area = soup.select('div.card_area') 

    for title_area in titles_area:
        title_text=title_area.select('div.con>div.con_top>div.tit_area>a.tit>span.inner>strong')[0].get_text().replace("  ", "").replace("\n", "").strip()
        article_id=parse_qs(urlparse(title_area.select('div.con>div.con_top>div.tit_area>a.tit')[0]['href']).query)['articleid'][0]     
        title_url="https://cafe.naver.com/hansicgu/"+str(article_id)
        image_url=title_area.select('div.movie-img>a>img')[0]['src']

        result_title.append(unicodedata.normalize('NFC',title_text))
        result_url.append(title_url)
        result_image.append(image_url)
       
    html = requests.get(url, headers = headers, params = params2)
    soup = BeautifulSoup(html.text, 'html.parser')
    titles_area = soup.select('div.card_area')  #W
    
    for title_area in titles_area:
        title_text=title_area.select('div.con>div.con_top>div.tit_area>a.tit>span.inner>strong')[0].get_text().replace("  ", "").replace("\n", "").strip()
        article_id=parse_qs(urlparse(title_area.select('div.con>div.con_top>div.tit_area>a.tit')[0]['href']).query)['articleid'][0]
        title_url="https://cafe.naver.com/hansicgu/"+str(article_id)
        image_url=None
        try:
            image_url=title_area.select('div.movie-img>a>img')[0]['src']
        except:
            image_url="https://cafeskthumb-phinf.pstatic.net/MjAyMjAzMjJfNjYg/MDAxNjQ3OTI3NjgxNzI0.4dVbmaEr6YXzMzZYF0ztA3QrqH6v8ZmpOZKNvvsqjYEg.I2hdAXCgLbPg0KcZw3dGmdKv8xFYtSxg3VrEwI-rztkg.GIF/bottomLogo.gif?type=w1080"

        result_title.append(unicodedata.normalize('NFC',title_text))
        result_url.append(title_url)
        result_image.append(image_url)

    return result_title, result_url, result_image
 
def new_article_detect_hansicgu(titles, urls, images):
    log("comparing hansicgu")
    try:
        lines = [line.rstrip('\n') for line in open('hansicgu.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    result_url = []
    result_image = []

    with open('hansicgu.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title, url, image in zip(titles, urls, images):
            check = 0
            for line in lines:
                if title in line:
                    check = 1
            if check == 0:
                result_title.append(title)
                result_url.append(url)
                result_image.append(image)
            f.write(title  + '\n')
            
    return result_title, result_url, result_image

  
## 스팀앱 ##
def parse_steamapp():
    log("scaning steamapp")
    headers = { 
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    result_title = []
    result_url = []
    result_image = []
    result_official = []

    url = 'https://steamapp.net/hangul'

    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    titles_area = soup.select('div.app') # 게시글
    
    for title_area in titles_area:
        title_text=title_area.select('div.title>div.item_title>a._app_name')[0]['title'].replace("  ", "").replace("\n", "").strip()
        article_id=title_area.select('div.title>div.item_title>a._app_name')[0]['href']
        title_url="https://steamapp.net"+str(article_id)
        image_url=title_area.select('div.title>div.item_title>a._app_header_image_link>img')[0]['src']   
        official=title_area.select('div.hangul>em')[0].get_text()
       
        result_title.append(unicodedata.normalize('NFC',title_text))
        result_url.append(title_url)
        result_image.append(image_url)
        result_official.append(official)

    return result_title, result_url, result_image, result_official
 

def new_article_detect_steamapp(titles, urls, images, officials):
    log("comparing steamapp")
    try:
        lines = [line.rstrip('\n') for line in open('steamapp.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    result_url = []
    result_image = []
    result_official = []

    with open('steamapp.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title, url, image, official in zip(titles, urls, images, officials):
            check = 0
            title_text = title+" "+image
            for line in lines:
                if title_text in line:
                    check = 1
            if check == 0:
                result_title.append(title)
                result_url.append(url)
                result_image.append(image)
                result_official.append(official)
            f.write(title_text  + '\n')
            
    return result_title, result_url, result_image, result_official

## 아카 유즈 ##
def parse_arka_use():
    log("scaning 아카유즈")
    headers = { # 헤더를 넣지 않아도 작동하는 것을 확인했습니다.
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }

    result_title = []
    result_url = []
    result_image = []
    url = 'https://arca.live/b/yuzusoft?category=%ED%95%9C%EA%B5%AD%EC%96%B4%ED%99%94%20%ED%8C%A8%EC%B9%98'

    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    titles_area = soup.select('a[class="vrow column"]') 
    
    for title_area in titles_area:
        title_text=title_area.select('div.vrow-inner span.title')[0].get_text().replace("  ", "").replace("\n", "").strip()     
        title_url="https://arca.live"+title_area['href'].split("?")[0]
        image_url=None
        try:
            image_url=title_area.select('div.vrow-preview img')[0]['src']
        except:
            image_url="https://cdn.sketchpan.com/member/d/dlawn8/draw/1298343920734/0.png"
       
        result_title.append(unicodedata.normalize('NFC',title_text))
        result_url.append(title_url)
        result_image.append(image_url)


    return result_title, result_url, result_image
 

def new_article_detect_arka_use(titles, urls, images):
    log("comparing 아카유즈")
    try:
        lines = [line.rstrip('\n') for line in open('arkause.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    result_url = []
    result_image = []


    with open('arkause.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title, url, image in zip(titles, urls, images):
            check = 0
            for line in lines:
                if title in line:
                    check = 1
            if check == 0:
                result_title.append(title)
                result_url.append(url)
                result_image.append(image)
            f.write(title  + '\n')
            
    return result_title, result_url, result_image

## 스위치 ##
def parse_switch():
    headers = { # 헤더를 넣지 않아도 작동하는 것을 확인했습니다.
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    log("scaning nintendo eshop")
    result_title = []
    result_url = []
    result_image = []

    url = 'https://store.nintendo.co.kr/games/all-released-games'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    titles_area = soup.select('div.category-product-item') # 게시글
    
    for title_area in titles_area:    
        title_text=title_area.select('div.category-product-item-info>div.category-product-item-title>a.category-product-item-title-link')[0].get_text().replace("  ", "").replace("\n", "").strip()
        title_url=title_area.select('div.category-product-item-info>div.category-product-item-title>a.category-product-item-title-link')[0]['href']
        image_url=title_area.select('div.category-product-item-img>a>span.product-image-container>span.product-image-wrapper>img')[0]['data-src']
        
        result_title.append(unicodedata.normalize('NFC',title_text))
        result_url.append(title_url)
        result_image.append(image_url)

    return result_title, result_url, result_image

def new_article_detect_switch(titles, urls, images):
    log("comparing nintendo eshop")
    try:
        lines = [line.rstrip('\n') for line in open('switch.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    result_url = []
    result_image = []

    with open('switch.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title, url, image in zip(titles, urls, images):
            check = 0
            for line in lines:
                if title in line:
                    check = 1
            if check == 0:
                result_title.append(title)
                result_url.append(url)
                result_image.append(image)
            f.write(title  + '\n')
            
    return result_title, result_url, result_image 



## 스위치 일본 ##
def parse_switch_jpn():
    headers = { # 헤더를 넣지 않아도 작동하는 것을 확인했습니다.
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    log("scaning nintendo eshop jpn")
    result_title = []
    result_url = []
    result_image = []

    for page in range(1,3):
        url = 'https://store-jp.nintendo.com/list/software/?srule=new-arrival&start='+str(page)
    
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        titles_area = soup.select('li.c-productList--item') # 게시글
    
        for title_area in titles_area:
            title_text=title_area.select('a.c-productList--item__link')[0]['title']
            title_url="https://store-jp.nintendo.com/"+title_area.select('a.c-productList--item__link')[0]['href']
            image_url=title_area.select('a.c-productList--item__link>div.c-productList--item__image>div.c-productList--item__imageItem>div.c-itemImage>img')[0]['src']
        
            result_title.append(unicodedata.normalize('NFC',title_text))
            result_url.append(title_url)
            result_image.append(image_url)

        time.sleep(0.5)
    return result_title, result_url, result_image

def new_article_detect_switch_jpn(titles, urls, images):
    log("comparing nintendo eshop jpn")
    try:
        lines = [line.rstrip('\n') for line in open('switch_jpn.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    result_url = []
    result_image = []

    with open('switch_jpn.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title, url, image in zip(titles, urls, images):
            check = 0
            for line in lines:
                if title in line:
                    check = 1
            if check == 0:
                result_title.append(title)
                result_url.append(url)
                result_image.append(image)
            f.write(title  + '\n')
            
    return result_title, result_url, result_image 


## 스위치 미국 ##
def parse_switch_eng():
    headers = { # 헤더를 넣지 않아도 작동하는 것을 확인했습니다.
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    log("scaning nintendo eshop eng")
    result_title = []
    result_url = []
    result_image = []

    for page in range(1,2):
        url = 'https://www.nintendo.com/store/games/#p=1&sort=rd'#+str(page)
    
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        titles_area = soup.select('div[class^="BasicTilestyles__Container"]') # 게시글
        log(len(titles_area))


        for title_area in titles_area:
            title_text=title_area.select('a')[0]['aria-label']
            title_url=title_area.select('a')[0]['href']

            log(title_text)

            image_url="https://cdn.sketchpan.com/member/d/dlawn8/draw/1298343920734/0.png"
            
            result_title.append(unicodedata.normalize('NFC',title_text))
            result_url.append(title_url)
            result_image.append(image_url)

        time.sleep(0.5)
    return result_title, result_url, result_image

def new_article_detect_switch_eng(titles, urls, images):
    log("comparing nintendo eshop eng")
    try:
        lines = [line.rstrip('\n') for line in open('switch_jpn.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    result_url = []
    result_image = []

    check = 0
    with open('switch_jpn.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title, url, image in zip(titles, urls, images):
            check = 0
            for line in lines:
                if title in line:
                    check = 1
            if check == 0:
                result_title.append(title)
                result_url.append(url)
                result_image.append(image)
            f.write(title  + '\n')
            
    return result_title, result_url, result_image 


## 프리게임DB ##
def parse_freedb():
    log("scaning free game db")
    result_title = []
    result_url = []
    result_image = []
    
    url = 'https://freegame.tistory.com/rss'
    feeds = feedparser.parse(url)
    
    for feed in feeds.entries:     
        title_text=feed.title
        title_url=feed.link
        image_url=feed.description

        result_title.append(unicodedata.normalize('NFC',title_text))
        result_url.append(title_url)
        result_image.append(image_url)

    time.sleep(0.5)
    return result_title, result_url, result_image

def new_article_detect_freedb(titles, urls, images):
    log("comparing free game db")
    try:
        lines = [line.rstrip('\n') for line in open('freegame.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    result_url = []
    result_image = []

    check = 0
    with open('freegame.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title, url, image in zip(titles, urls, images):
            check = 0
            if '인기 작품 순위' in title:
                check = 1
            #if '한글판' in image:
            #    check = 1
            for line in lines:
                if title in line:
                    check = 1
            if check == 0:
                result_title.append(title)
                result_url.append(unquote_plus(url))
                result_image.append(image)
            f.write(title  + '\n')
            
    return result_title, result_url, result_image 

if __name__ == '__main__':
    bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())
    __text_remove__ = " ||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _ "
@bot.event
async def on_ready():
    log(f'Login bot: {bot.user}')
    Test = False
    if Test is True:
        channel_hansicgu_discord = bot.get_channel(False) 
        channel_hansicgu = bot.get_channel(False) 
        channel_nintendo = bot.get_channel(False) 
        channel_freegame = bot.get_channel(False) 
        channel_arkause = bot.get_channel(False) 
    else:
        channel_hansicgu_discord = bot.get_channel(False) 
        #channel_hansicgu_discord = bot.get_channel(False) 
        channel_hansicgu = bot.get_channel(False) 
        channel_nintendo = bot.get_channel(False) 
        channel_freegame = bot.get_channel(False) 
        channel_steamapp = bot.get_channel(False) 
        channel_arkause = bot.get_channel(False) 
    #await channel.send("봇 부팅")
    while True:
        titles = []
        urls = []
        images = []
        officials = []


        result_title = []
        result_urls = []
        result_images = []
        result_officials = []
        
        
        titles, urls, images = parse_arka_use()
        result_title, result_urls, result_image = new_article_detect_arka_use(titles, urls, images)
        for title , url, image in zip(result_title, result_urls, result_image):
            log("new: "+title)
            params = {
                'author' : '아카라이브 유즈소프트 채널', # 카페 ID
                'title' : title,
                'color' : '42464F',
                'image' : unquote_plus(image),
                'redirect' : url
            }
            await channel_arkause.send("`아카라이브 유즈소프트 채널` "+title+"\n링크: <"+url+">"+__text_remove__+"https://embed.rauf.workers.dev/?"+urlencode(params))
        await asyncio.sleep(5)

        titles, urls, images = parse_hansicgu()
        result_title, result_urls, result_image = new_article_detect_hansicgu(titles, urls, images)
        for title , url, image in zip(result_title, result_urls, result_image):
            log("new: "+title)
            params = {
                'author' : '한식구', # 카페 ID
                'title' : title,
                'color' : 'ffffff',
                'image' : unquote_plus(image),
                'redirect' : url
            }
            await channel_hansicgu_discord.send("`한식구` "+title+"\n링크: "+url+__text_remove__+"https://embed.rauf.workers.dev/?"+urlencode(params))
            
            await channel_hansicgu.send("`한식구` "+title+"\n링크: "+url+__text_remove__+"https://embed.rauf.workers.dev/?"+urlencode(params))
        await asyncio.sleep(5)

        titles, urls, images, officials = parse_steamapp()
        result_title, result_urls, result_image, result_officials = new_article_detect_steamapp(titles, urls, images, officials)
        for title , url, image, official in zip(result_title, result_urls, result_image, result_officials):
            log("new: "+title)
            params = {
                'author' : '스팀앱', # 카페 ID
                'title' : str(title+" · 스팀"),
                'color' : '0B2161',
                'image' : unquote_plus(image),
                'redirect' : url
            }
            await channel_steamapp.send("`스팀앱` "+title+" 한국어화 ("+official+")"+"\n링크: <"+url+">"+__text_remove__+"https://embed.rauf.workers.dev/?"+urlencode(params))
        await asyncio.sleep(5)
        #https://embed.rauf.workers.dev/
        
        #switch fommer part
        titles, urls, images = parse_switch()
        result_title, result_urls, result_image = new_article_detect_switch(titles, urls, images)
        
        for title , url, image in zip(result_title, result_urls, result_image):
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            language_support = soup.select('div[class="product-attribute supported_languages"]>div.product-attribute-val')[0].get_text()
            await asyncio.sleep(5)
            if '한국' in language_support:
                log("new: "+title)
                params = {
                    'author' : '한국닌텐도 eShop', # 카페 ID
                    'title' : title,
                    'color' : 'e60012',
                    'image' : unquote_plus(image),
                    'redirect' : url
                }
                await channel_nintendo.send("`Nintendo eShop` "+title+" 한국어 지원"+"\n링크: <"+url+">"+__text_remove__+"https://embed.rauf.workers.dev/?"+urlencode(params))
        await asyncio.sleep(5)

        titles, urls, images = parse_switch_jpn()
        result_title, result_urls, result_image = new_article_detect_switch_jpn(titles, urls, images)
        
        for title , url, image in zip(result_title, result_urls, result_image):
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            language_support = soup.select('table.productDetail--spec')[0].get_text()
            await asyncio.sleep(5)
            if '韓国' in language_support:
                log("new: "+title)
                params = {
                    'author' : '일본닌텐도 eShop', # 카페 ID
                    'title' : title,
                    'color' : 'e60012',
                    'image' : unquote_plus(image),
                    'redirect' : url
                }
                await channel_nintendo.send("`Nintendo eShop` "+title+" 한국어 지원"+"\n링크: <"+url+">"+__text_remove__+"https://embed.rauf.workers.dev/?"+urlencode(params))
        await asyncio.sleep(5)


        titles, urls, images = parse_freedb()
        result_title, result_urls, result_image = new_article_detect_freedb(titles, urls, images)
        for title , url, image in zip(result_title, result_urls, result_image):
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            image_k = soup.select('meta[property="og:image"]')[0]['content']
            
            sh = pyshorteners.Shortener()
            log("new: "+title)

            params = {
                'author' : '프리게임 한글화 DC', # 카페 ID
                'title' : title,
                'color' : '6E6E6E',
                'image' : unquote_plus(image_k),
                'redirect' : sh.tinyurl.short(url)
            }
            await channel_freegame.send("`프리게임DB` "+title+" 한국어화"+"\n링크: <"+sh.tinyurl.short(url)+">"+__text_remove__+"https://embed.rauf.workers.dev/?"+urlencode(params))
        await asyncio.sleep(5)

        del officials
        del titles
        del urls
        del images

        del result_title
        del result_urls
        del result_images
        del result_officials
        log("pause")
        await asyncio.sleep(600)

    
#@bot.command()
#async def hello(message):
#    await message.channel.send('Hi!')
 
bot.run(Token)
