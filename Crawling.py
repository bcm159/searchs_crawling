import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import signaturehelper
import urllib


def get_header(method, uri, api_key, secret_key, customer_id):
    timestamp = str(round(time.time() * 1000))
    signature = signaturehelper.Signature.generate(timestamp, method, uri, SECRET_KEY)
    return {'Content-Type': 'application/json; charset=UTF-8', 'X-Timestamp': timestamp, 'X-API-KEY': API_KEY, 'X-Customer': str(CUSTOMER_ID), 'X-Signature': signature}

BASE_URL = 'https://api.searchad.naver.com'
API_KEY = '010000000074d47e4dd1f1f495f7e53907a34ed0499c2af68b5db7410149be263c9c35b772'
SECRET_KEY = 'AQAAAAB01H5N0fH0lfflOQejTtBJd7g/5nvMGfjD6cFdCid49A=='
CUSTOMER_ID = '2671614'

header = {'User-agent' : 'Mozila/2.0'}

#한달 검색량 리스트
month_pc_li = []
month_mobile_li = []
month_sum_li = []

#노출 1,2,3,4,5 리스트
titles_li1 = []
titles_li2 = []
titles_li3 = []
titles_li4 = []
titles_li5 = []

#지식in 날짜, 조회수 리스트
know_li1 = []
know_li2 = []
know_li3 = []

know_count = 0

words = input('키워드들을 입력해주세요 : ')

month_pc_num = 0
month_mobile_num = 0
month_sum_num = 0

keyword_li = words.split(',')

for keyword in keyword_li:
    #한글로 인한 오류 방지
    urllib.parse.quote(keyword)
    uri = '/keywordstool'
    method = 'GET'
    response = requests.get(BASE_URL + uri + f'?hintKeywords={keyword}&showDetail=1', headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))
    test = response.json()['keywordList'][0]


    if(test.get('relKeyword')) == keyword:
        month_pc_num = test.get('monthlyPcQcCnt')
        month_mobile_num = test.get('monthlyMobileQcCnt')
        month_sum_num = month_pc_num + month_mobile_num

    month_pc_li.append(month_pc_num)
    month_mobile_li.append(month_mobile_num)
    month_sum_li.append(month_sum_num)


    # 크롤링

    response = requests.get(f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={keyword}", headers=header)
    html = response.text

    soup = BeautifulSoup(html,'html.parser')
    #검색시 블카공 순서 가져오기
    titles = soup.select('.tab')

    count = 0


    for link in titles:
        if count == 0:  titles_li1.append(link.text)
        elif count == 1:    titles_li2.append(link.text)
        elif count == 2:    titles_li3.append(link.text)
        elif count == 3:    titles_li4.append(link.text)
        elif count == 4:    titles_li5.append(link.text)
        if count == 5:  break
        count = count + 1


#지식인 날짜,조회수 조회

    response = requests.get(
        f"https://search.naver.com/search.naver?ssc=tab.kin.kqna&where=kin&sm=tab_jum&query={keyword}", headers=header)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    info_sub_li = soup.select('a.question_text')

    for info_sub in info_sub_li:
        if know_count < 3:
            res = requests.get(f"{info_sub['href']}", headers=header)
            know_html = res.text
            know_soup = BeautifulSoup(know_html, 'html.parser')

            know_info = know_soup.select('span.c-userinfo__info')

            if know_count == 0: know_li1.append(know_info[0].text + ' ' + know_info[1].text)
            elif know_count == 1:   know_li2.append(know_info[0].text + ' ' + know_info[1].text)
            elif know_count == 2:   know_li3.append(know_info[0].text + ' ' + know_info[1].text)

            know_count = know_count + 1

        else:
            know_count = 0
            break

result_dic = {
    '키워드' : keyword_li,
    '월간검색수' : month_pc_li,
    '월간검색수(모바일)' : month_mobile_li,
    '합계' : month_sum_li,
    '노출1' : titles_li1,
    '노출2' : titles_li2,
    '노출3' : titles_li3,
    '노출4' : titles_li4,
    '노출5' : titles_li5,
    '지식in1등(날짜/조회수)' : know_li1,
    '지식in2등(날짜/조회수)' : know_li2,
    '지식in3등(날짜/조회수)' : know_li3
}

#엑셀 생성
df = pd.DataFrame(result_dic, columns=['키워드','월간검색수','월간검색수(모바일)','합계','노출1','노출2','노출3','노출4','노출5','지식in1등(날짜/조회수)','지식in2등(날짜/조회수)','지식in3등(날짜/조회수)'])
excel_writer = pd.ExcelWriter('C:/Users/bcm15/OneDrive/바탕 화면/브랜딩/마케팅지도.xlsx',engine='xlsxwriter')
df.to_excel(excel_writer, index=False, sheet_name='마케팅지도')
excel_writer.close()

