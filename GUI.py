from UAssist import Myassistant
from actions import Actions
from tkinter import *
import threading
import os

class MyThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting " + self.name)
        thread_UAssist(Myassistant.thread)
        print("\nExiting " + self.name)


def thread_UAssist(threadExe):
    if threadExe == 0:
        Myassistant.thread = 1
        Actions.btn_text.set('Stop')
        Actions.status_text.set('Listening')
        Myassistant().main()


def callUAssist():
    thread1 = MyThread(1, "UAssist")
    if Myassistant.thread == 1:
        Myassistant.thread = 2
        Actions.status_text.set('Now try hotword to exit')
        return

    thread1.start()


root = Tk()
# test 1 line
root.tk.call('encoding', 'system', 'utf-8')

root.title("UAssist")
frame1 = Frame(root, bd=4)
frame1.pack(side=TOP, expand="yes", fill=BOTH)

frame2 = Frame(root, bd=4)
frame2.pack(side=TOP)

frame3 = Frame(root, bd=4)
frame3.pack(side=TOP)

frame4 = Frame(root, bd=4)
frame4.pack(side=TOP)

# chat box
Actions.chatScroll = Scrollbar(frame1)
Actions.chatBox = Text(frame1, wrap='word', state='disabled', yscrollcommand=Actions.chatScroll.set, width=50)
Actions.chatScroll.configure(command=Actions.chatBox.yview)
Actions.chatBox.pack(side=LEFT, fill=BOTH, expand="yes")
Actions.chatScroll.pack(side=RIGHT, fill=Y)
Actions.chatLast = 0
'''
# image box image.gif=237
filePath = '{}/resource/Image/image.gif'.format(os.path.realpath(os.path.join(__file__, '..')))
frames = [PhotoImage(file=filePath, format='gif -index %i' % i) for i in range(237)]
def update(ind):
    frame = frames[ind]
    ind += 1
    if ind == 237:
        ind = 1
    imageBox.configure(image=frame)
    frame1.after(60, update, ind)
imageBox = Label(frame1)
imageBox.pack()
frame1.after(0, update, 0)
'''
# text box
textView = Label(frame2, text="Input: ")
textView.pack(side=LEFT)
Actions.text_text = StringVar()
textBox = Label(frame2, textvariable=Actions.text_text, bd=0, width=40, bg="pink")
textBox.pack(side=RIGHT, expand="yes")

# status box
statusView = Label(frame3, text="State: ")
statusView.pack(side=LEFT)
Actions.status_text = StringVar()
statusBox = Label(frame3, textvariable=Actions.status_text, bd=0, width=40, bg="pink")
statusBox.pack(side=RIGHT, expand="yes")

# start/stop
Actions.btn_text = StringVar()
button = Button(frame4, textvariable=Actions.btn_text, fg="black", command=callUAssist)
Actions.btn_text.set("Start")
Actions.status_text.set('Not Listening')
button.pack(side=TOP)
root.mainloop()
