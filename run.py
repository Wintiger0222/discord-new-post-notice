import discord
from discord.ext import commands
import requests, time, re
from bs4 import BeautifulSoup
import unicodedata


## requests와 BeautifulSoup으로 카페 게시글 목록을 불러오는 함수 ##
def bs(url, page):
    headers = { # 헤더를 넣지 않아도 작동하는 것을 확인했습니다.
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
    params_test = {
        'search.clubid' : '10050146', # 카페 ID
        # 'search.menuid' : '8', # 메뉴 ID
        'search.boardtype' : 'L', # 보드타입 (반드시 필요로 하는 것은 아닌 것 같습니다.)
        #'search.page' : page # 불러올 페이지
    }    
    
    params = {
        'search.clubid' : '16259867', # 카페 ID
        #'search.menuid' : '8', # 메뉴 ID
        'search.boardtype' : 'L', # 보드타입 (반드시 필요로 하는 것은 아닌 것 같습니다.)
        'search.page' : page # 불러올 페이지
    }
    html = requests.get(url, headers = headers, params = params)
    soup = BeautifulSoup(html.text, 'html.parser')
    return soup

## 게시글 제목과 리플 수를 파싱하여 리플 수가 일정 이상인 경우만 추출하는 함수 ##
def parse(url):
    print("scaning")
    page = 0
    result_title = []
    result_reply = []
    
    soup = bs(url, page)
    titles = soup.select('td.td_article>div.board-list>div.inner_list>a.article') # 게시글 제목
    for title in titles:
        title_text=title.get_text().replace("  ", "").replace("\n", "").strip()
        result_title.append(unicodedata.normalize('NFC',title_text))
        #print(title_text)
    time.sleep(0.5)
    return result_title
 
## TXT 파일로 결과를 저장하고 텔레그램으로 새 글을 알리는 함수 ##
def new_article_detect(titles):
    print("comparing")
    try:
        lines = [line.rstrip('\n') for line in open('ncafe.txt', 'r', encoding='utf8')]
    except: # 파일이 존재하지 않는 경우를 예외처리합니다. (처음 실행하는 경우 에러가 발생하기 때문입니다.)
        lines = ['no data']
    
    result_title = []
    check = 0
    #for title in titles:
       # print(title)
    with open('ncafe.txt', 'w', encoding='utf8') as f: # TXT 파일을 업데이트합니다.
        for title in titles:
            check = 0
            for line in lines:
                if title in line:
                    print(line+"VS"+title)
                    check = 1
            #print(check)
            if check == 0:
                result_title.append(title)
            f.write(title  + '\n')
            
    return result_title
    


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())
    #url = 'https://m.cafe.naver.com/ArticleAllListAjax.nhn'
    url = 'https://cafe.naver.com/ArticleList.nhn'
    
@bot.event
async def on_ready():
    print(f'Login bot: {bot.user}')
    channel = bot.get_channel(1103301381319827518)
    await channel.send("hello")
    while True:
        result_title = []
        titles = []
        check = 0
        titles = parse(url)
        result_title = new_article_detect(titles)
        for title in result_title:
            print(title)
            await channel.send(title)
        time.sleep(60)
        

#@bot.command()
#async def hello(message):
#    await message.channel.send('Hi!')
 
bot.run('MTEyMTM4NjgxNTI3OTA3MTI4Mg.GTa4-y.C2KjRYv1f06lm7ArdEgg45N1GMC_saLqZfiJXw')