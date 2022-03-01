#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 15:01:15 2022

@author: alejandro
"""

from random import randint
from multiprocessing import Process
from multiprocessing import BoundedSemaphore
from multiprocessing import Semaphore
from multiprocessing import Lock
from multiprocessing import current_process
from multiprocessing import Value
from multiprocessing import Array
from multiprocessing import Manager

N = 10
NPROD = 2

def add_data(storage, index, data, mutex):
    mutex.acquire()
    try:
        storage[index] = data
        #print("p", index, data, flush = True)
    finally:
        mutex.release()
        
# =============================================================================
# def get_data(storage, index, mutex): # No sé ni si va a haber que usarlo
#     mutex.acquire()
#     try:
#         data = storage[index]
#         #for i in range(index.value):
#         #    storage[i] = storage[i + 1]
#         #storage[index.value] = -1
#     finally:
#         mutex.release()
#     return data
# =============================================================================

def producer(storage, index, list_empty, list_non_empty, mutex):
    #producidos = []
    for v in range(N):
        list_empty[index].acquire()
        data = randint(0, 10)
        data += storage[index]
        add_data(storage, index, data, mutex)
        #producidos.append(data)
        list_non_empty[index].release()
    list_empty[index].acquire()
    add_data(storage, index, -1, mutex)
    list_non_empty[index].release()
    #print(producidos)

def consumer(storage, list_empty, list_non_empty, mutex, merge): # Como lo tengo ahora no usa muex, no sé si hay que añadirlo
    for i in range(NPROD):
        list_non_empty[i].acquire()

    while list(storage) != [-1]*NPROD:
        minimum = 2**64-1 # sys.maxsize si se importa system
        index = -1
        for i in range(NPROD): 
            if storage[i] != -1 and storage[i] < minimum:
                index = i
                minimum = storage[i]
        #print("c", index, minimum, flush = True)
        merge.append(minimum)
        #print(merge)
        list_empty[index].release()
        list_non_empty[index].acquire()

    print(merge)
        

def main():
    storage = Array("i", NPROD)
    merge = []
    for i in range(NPROD):
        storage[i] = 0
    
    
    
    list_non_empty = [Semaphore(0) for i in range(NPROD)]
    list_empty = [BoundedSemaphore(1) for i in range(NPROD)]
    mutex = Lock()
    
    prodlst = [Process(target = producer, args = (storage, index, list_empty, list_non_empty, mutex)) for index in range(NPROD)]

    # Sólo hay un consumidor
    cons = Process(target = consumer, args = (storage, list_empty, list_non_empty, mutex, merge))

    for p in prodlst:
        p.start()
    cons.start()
    
    for p in prodlst:
        p.join()
    cons.join()
    
    #print(merge)

if __name__ == "__main__":
    main()
    




