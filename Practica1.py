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
from multiprocessing import Value
from multiprocessing import Array

N = 10
NPROD = 3
rand_lower = 0
rand_upper = 10

# Quítese el comentario de las líneas 23, 29 y 34 si se quieren ver las listas con los valores producidos por cada productor
def producer(storage, index, list_empty, list_non_empty): 
    #producidos = []
    for v in range(N):
        list_empty[index].acquire()
        data = randint(rand_lower, rand_upper)
        data += storage[index]
        storage[index] = data # add data
        #producidos.append(data)
        list_non_empty[index].release()
    list_empty[index].acquire()
    storage[index] = -1
    list_non_empty[index].release()
    #print("Productor", index, ": ", producidos, flush = True)

def consumer(storage, list_empty, list_non_empty, merge): 
    for i in range(NPROD):
        list_non_empty[i].acquire()

    while list(storage) != [-1]*NPROD:
        minimum = float("inf")
        index = -1
        for i in range(NPROD): 
            if storage[i] != -1 and storage[i] < minimum:
                index = i
                minimum = storage[i]
        merge.append(minimum)
        list_empty[index].release()
        list_non_empty[index].acquire()

    print("Merge: ", merge, flush = True)
        

def main():
    storage = Array("i", NPROD)
    merge = []
    for i in range(NPROD):
        storage[i] = 0
    
    list_non_empty = [Semaphore(0) for i in range(NPROD)]
    list_empty = [BoundedSemaphore(1) for i in range(NPROD)]
    
    prodlst = [Process(target = producer, args = (storage, index, list_empty, list_non_empty)) for index in range(NPROD)]

    # Sólo hay un consumidor
    cons = Process(target = consumer, args = (storage, list_empty, list_non_empty, merge))

    for p in prodlst:
        p.start()
    cons.start()
    
    for p in prodlst:
        p.join()
    cons.join()
    

if __name__ == "__main__":
    main()
    




