#!/usr/bin/env python3

import os
import sys
import numpy as np
from multiprocessing import Process, Queue


def detect(q, pointer, inputList):
    print("Detect method called - Pointer: " + str(pointer))
    # Initialize variables
    # 0x1ACFFC1D
    sync_header = np.array([1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1])
    sync_header_len = len(sync_header)
    packet_size = 16*8 # Packetsize in bit
    pointer_temp = 0
    try:
        correlated = np.correlate(inputList[pointer:-1], sync_header, mode='full')
    except ValueError:
        q.put(pointer)
        return
    # Loop until array end is reached
    while len(inputList)-pointer > sync_header_len + packet_size:
        try:
            corrupted_sync_bit = sync_header.__xor__(inputList[correlated[pointer_temp:-1].argmax()-len(sync_header)+1+pointer_temp+pointer:correlated[pointer_temp:-1].argmax()+1+pointer_temp+pointer])
            corrupted_sync_bit_count = corrupted_sync_bit.sum()
        except ValueError:
            print("Correlation failed")
            q.put(pointer)
            return
        print("-----------------------------------")
        if (corrupted_sync_bit_count == 0) and (len(inputList[correlated[pointer_temp:-1].argmax()+2+pointer_temp+pointer:correlated[pointer_temp:-1].argmax()+2+packet_size+pointer_temp+pointer]) == packet_size):
            print("Sync header found!")
            print("Input array size: " + str(len(inputList)))
            print("Correlated array-size: " + str(correlated[pointer_temp:-1].size))
            print("Correlated argmax index: " + str(correlated[pointer_temp:-1].argmax()))
            print("Correlated argmax value: " + str(correlated[correlated[pointer_temp:-1].argmax()+pointer_temp]))
            print(inputList[correlated[pointer_temp:-1].argmax()-len(sync_header)+1+pointer_temp+pointer:correlated[pointer_temp:-1].argmax()+1+pointer_temp+pointer])
            print(inputList[correlated[pointer_temp:-1].argmax()+1+pointer_temp+pointer:correlated[pointer_temp:-1].argmax()+1+packet_size+pointer_temp+pointer])
            a = inputList[correlated[pointer_temp:-1].argmax()+1+pointer_temp+pointer:correlated[pointer_temp:-1].argmax()+1+packet_size+pointer_temp+pointer]
            s = ''.join([str(i) for i in a])
            print(int(s, 2).to_bytes(len(s) // 8, byteorder='big'))
            pointer_temp = correlated[pointer_temp:-1].argmax()+2+packet_size+pointer_temp
            pointer = pointer + pointer_temp
            print("Pointer: " + str(pointer))
        else:
            print("Sync header not found!")
            print("Corrupted sync bit count: " + str(corrupted_sync_bit_count))
            pointer = len(inputList) - sync_header_len
            print("Pointer: " + str(pointer))
    q.put(pointer)
    return
