import threading

def func(index, event_for_stop):
    for i in range(index, index + 10):

        if (event_for_stop.isSet()):
            print "break"
            break

        print i

    event_for_stop.set()

event_for_stop = threading.Event()

thread1 = threading.Thread(target=func, args=(0, event_for_stop))
thread2 = threading.Thread(target=func, args=(10, event_for_stop))
thread3 = threading.Thread(target=func, args=(20, event_for_stop))

thread1.start()
thread2.start()
thread3.start()