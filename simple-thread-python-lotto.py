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

def worker (semaphore, draw, results) :
    
    with semaphore :
        print (f"Worker get_info ({draw}) started")
        result = get_info (draw)
        results.append (result)
        print (f"Worker get_info ({draw}) finished")
        

def get_info (draw) :
    global headers;
    global url_info;
    
    result = []
    
    try :
        url = url_info.format (draw)
        print ("get info : {}".format (url))
        result_html = requests.get (url, headers = headers).text

        info_regex = r"<div class=\"win_result\">(.*?)<div class=\"num win\">(.*?)<div class=\"num bonus\">(.*?)</div>"
        info_matches = re.search (info_regex, result_html, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        info_match_html = info_matches.group (0)

        ball_regex = r"<span class=\"ball_645(.*?)\".*?>(.*?)</span>"
        ball_compile = re.compile (ball_regex, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        ball_matches = ball_compile.findall (info_match_html)
        
        for draw_match in ball_matches :
             result.append (draw_match [1])
             
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

        draw_regex = r"<option value=\"(.*?)\".*?>(.*?)</option>"
        draw_compile = re.compile (draw_regex, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        draw_matches = draw_compile.findall (list_match_html)
        
        n = 0
        for draw_match in draw_matches :
             n += 1
             result.append (draw_match [0])
             if max == n : break
             
    except Exception as e :
        print (str (e))
    
    return result;

if __name__ == '__main__' :
    
    # ????????? ????????? ???????????? ???????????????.
    results = []
    semaphore = threading.Semaphore (max_threads)

    draws = get_list (max_list)
    print (draws)
    
    # ?????? ?????? ????????? ?????? ???????????? ???????????????.
    threads = []
    for draw in draws :
        threads.append (threading.Thread (target = worker, args = (semaphore, draw, results)))

    # ????????? ??????????????? ???????????????.
    for thread in threads :
        thread.start ()

    # ?????? ???????????? ?????? ????????? ???????????????.
    for thread in threads :
        thread.join ()

    # ????????? ????????? ?????? ?????? ????????? ???????????????.
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
     
    print ("Stats (win, ?????? ?????? ??????) : {}".format (stats ["win"]))
    print ("Stats (all, ?????? ??? ????????? ?????? ?????? ??????) : {}".format (stats ["all"]))

    