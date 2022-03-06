#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 10:05:55 2022

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

K = 5 # BUFFER, K >= 1, K = 1 es el caso anterior
N = 10
NPROD = 3

def add_data(storage, index, buffer_indices, data, mutex):
    mutex.acquire()
    try:
        storage[index*K+buffer_indices[index]] = data
        buffer_indices[index] += 1
        print("p", index, data, flush = True)
        print("s", list(storage), flush = True)
        print("bf", list(buffer_indices), flush = True)
    finally:
        mutex.release()
        
# =============================================================================
# def get_data(storage, index, mutex):
#     mutex.acquire()
#     try:
#         data = storage[index]
#         for i in range(index.value):
#             storage[i] = storage[i + 1]
#         storage[index.value] = -1
#     finally:
#         mutex.release()
#     return data
# =============================================================================

# Esto hay que mirarlo
def producer(storage, index, buffer_indices, list_empty, list_non_empty, mutex):
    #producidos = []
    data = 0
    for v in range(N):
        list_empty[index].acquire()
        rand = randint(0, 10)
        data += rand
        add_data(storage, index, buffer_indices, data, mutex)
        #producidos.append(data)
        list_non_empty[index].release()
    list_empty[index].acquire()
    #storage[index*K+buffer_indices[index]] = -1 # buffer_indices[index] = 0
    add_data(storage, index, buffer_indices, -1, mutex) # buffer_indices[index] = 0
    list_non_empty[index].release()
    #print(producidos, flush = True)

def consumer(storage, buffer_indices, list_empty, list_non_empty, mutex, merge): # Como lo tengo ahora no usa muex, no sé si hay que añadirlo
    for i in range(NPROD):
        list_non_empty[i].acquire()

    while [storage[i*K] for i in range(NPROD)] != [-1]*NPROD:
        minimum = float("inf")
        index = -1
        mutex.acquire()
        try:
            for i in range(NPROD): 
                if storage[i*K] != -1 and storage[i*K] < minimum:
                    index = i
                    minimum = storage[i*K]
            print("c", index, minimum)
            # Creo que hay que usar un lock
            buffer_indices[index] -= 1
            for i in range(buffer_indices[index]):
                storage[index*K+i] = storage[index*K+i+1]
            storage[index*K+buffer_indices[index]] = 0
            print("S", list(storage))
            print("BF", list(buffer_indices))
            # Este sería el fin del lock (a lo mejor no hace falta eh)
        finally:
            mutex.release()
        merge.append(minimum)
        list_empty[index].release()
        list_non_empty[index].acquire()        
        
    print("m: ", merge, flush = True)
        

def main():
    storage = Array("i", NPROD*K) # Puede que sea K+1 por el storage[i] = storage[i+1] del consumidor
    buffer_indices = Array("i", NPROD)
    merge = []
    for i in range(NPROD):
        storage[i] = 0
    
    
    
    list_non_empty = [Semaphore(0) for i in range(NPROD)]
    list_empty = [BoundedSemaphore(K) for i in range(NPROD)]
    mutex = Lock()
    
    prodlst = [Process(target = producer, args = (storage, index, buffer_indices, list_empty, list_non_empty, mutex)) for index in range(NPROD)]

    # Sólo hay un consumidor
    cons = Process(target = consumer, args = (storage, buffer_indices, list_empty, list_non_empty, mutex, merge))

    for p in prodlst:
        p.start()
    cons.start()
    
    for p in prodlst:
        p.join()
    cons.join()
    

if __name__ == "__main__":
    main()