# -*- coding: utf-8 -*-

import random
import threading
from time import sleep

def worker (num):
    
    # 여기에서 작업을 수행합니다.
    duration = (5 + random.randint (1, 10))
    print (f"Worker #{num} {duration} started")
    sleep (duration)
    print (f"Worker #{num} {duration} finished")

if __name__ == '__main__':
    
    # 실행 작업 카운트를 설정합니다. 
    jobs = 10
    
    # 실행 작업 카운트 만큼 스레드를 생성합니다.
    threads = [threading.Thread (target = worker, args = (i,)) for i in range (jobs)]

    # 생성한 스레드들을 시작합니다.
    for thread in threads :
        thread.start ()

    # 모든 스레드가 끝날 때까지 기다립니다.
    for thread in threads :
        thread.join ()

    print ("All workers finished")
