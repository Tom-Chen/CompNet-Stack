from Libraries import morse, utilities, gpio
from Constants import a_local, b_local
import queue, threading

recvqueue = queue.Queue()
transmitEvent = threading.Event()
transmitEvent.set()
receiveEvent = morse.Receive(recvqueue.put,transmitEvent,23)
while True:
    recv_message = recvqueue.get()
    print(recv_message)
    print(morse.reverse_translate(recv_message))
gpio.cleanup()