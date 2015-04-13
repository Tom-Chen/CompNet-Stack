from Libraries import morse, utilities, gpio
from Constants import a_local, b_local
import queue, threading

sendqueue = queue.Queue()
transmitEvent = threading.Event()
transmitEvent.set()
send_Thread = threading.Thread(target = morse.send,args = (sendqueue,transmitEvent,17))
send_Thread.start()
print("thread started")
sendqueue.put("4 ACES")
print("put something in the queue")
gpio.cleanup()