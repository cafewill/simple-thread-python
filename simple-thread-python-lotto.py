# -*- coding: utf-8 -*-

import re
import requests
import threading

max_list = 12
max_threads = 3;

headers = {
    "Content-Type" : "text/html; charset=UTF-8"
    , "Referer" : "https://dhlottery.co.kr/gameResult.do?method=byWin"
}
url_list = "https://dhlottery.co.kr/gameResult.do?method=byWin"
url_info = "https://dhlottery.co.kr/gameResult.do?method=byWin&drwNo={}"

def worker (semaphore, round, results) :
    
    with semaphore :
        print (f"Worker get_info ({round}) started")
        result = get_info (round)
        results.append (result)
        print (f"Worker get_info ({round}) finished")

def get_info (round) :
    global headers;
    global url_info;
    
    result = []
    
    try :
        url = url_info.format (round)
        print ("get info : {}".format (url))
        result_html = requests.get (url, headers = headers).text

        info_regex = r"<div class=\"win_result\">(.*?)<div class=\"num win\">(.*?)<div class=\"num bonus\">(.*?)</div>"
        info_matches = re.search (info_regex, result_html, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        info_match_html = info_matches.group (0)

        ball_regex = r"<span class=\"ball_645(.*?)\".*?>(.*?)</span>"
        ball_compile = re.compile (ball_regex, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        ball_matches = ball_compile.findall (info_match_html)
        
        for round_match in ball_matches :
             result.append (round_match [1])
             
    except Exception as e :
        print (str (e))
    
    return result;

def get_list (max) :
    global headers;
    global url_list;
    
    result = []
        
    try :
        url = url_list
        print ("get list : {}".format (url))
        result_html = requests.get (url, headers = headers).text

        list_regex = r"<select id=\"dwrNoList\".*?>(.*?)</select>"
        list_matches = re.search (list_regex, result_html, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        list_match_html = list_matches.group (0)

        round_regex = r"<option value=\"(.*?)\".*?>(.*?)</option>"
        round_compile = re.compile (round_regex, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        round_matches = round_compile.findall (list_match_html)
        
        n = 0
        for round_match in round_matches :
             n += 1
             result.append (round_match [0])
             if max == n : break
             
    except Exception as e :
        print (str (e))
    
    return result;

if __name__ == '__main__' :
    
    # 결과를 저장할 리스트를 생성합니다.
    results = []
    semaphore = threading.Semaphore (max_threads)

    rounds = get_list (max_list)
    print (rounds)
    
    # 실행 작업 카운트 만큼 스레드를 생성합니다.
    threads = []
    for round in rounds :
        threads.append (threading.Thread (target = worker, args = (semaphore, round, results)))

    # 생성한 스레드들을 시작합니다.
    for thread in threads :
        thread.start ()

    # 모든 스레드가 끝날 때까지 기다립니다.
    for thread in threads :
        thread.join ()

    # 수집된 결과로 당첨 번호 통계를 설정합니다.
    stats = {}
    stats ["win"] = {}
    stats ["all"] = {}
    for n in range (1, 45 + 1) : 
        stats ["win"][n] = 0;
        stats ["all"][n] = 0;

    for balls in results : 
        n = 0     
        for w in balls :
            n += 1
            stats ["all"][int (w)] += 1
            if n <= 6 : stats ["win"][int (w)] += 1     
     
    print ("Stats (win, 당첨 번호 통계) : {}".format (stats ["win"]))
    print ("Stats (all, 당첨 및 보너스 번호 포함 통계) : {}".format (stats ["all"]))

    