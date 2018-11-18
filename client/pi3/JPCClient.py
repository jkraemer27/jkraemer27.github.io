import socket
from utl.jpc_parser.JPCProtocol import JPCProtocol
import time
import threading
from tkinter import *


class JPCClientGUI:
    def __init__(self):
        self.root = Tk()
        #self.root.attributes("-fullscreen", True)
        self.message_text = StringVar()
        self.message_text.set("Welcome")
        self.configure_widgets()

    def configure_widgets(self):
        self.label = Label(self.root, textvariable=self.message_text,font=("Courier", 50), wraplength=500, justify=LEFT)
        self.label.pack()

    def run(self):
        self.root.mainloop()

    def flash_screen(self, color):
        self.label.configure(background=color)
        self.root.configure(background=color)

    def set_message(self, message):
        self.message_text.set(message)
        for i in range(0,10):
            self.flash_screen("white")
            time.sleep(.1)
            self.flash_screen("red")
            time.sleep(.1)
        self.flash_screen("white")


class JPCClient:
    def __init__(self, server_address):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((server_address, JPCProtocol.STANDARD_PORT))
        JPCProtocol(JPCProtocol.HELLO).send(self.server)
        self.gui = JPCClientGUI()
        threading.Thread(target=self.run).start()
        self.gui.run()

    def run(self):
        try:
            threading.Thread(target=self.send_heartbeats).start()
            running = True
            while running:
                data = self.server.recv(64000)
                if data:
                    data_list = JPCProtocol.decode(data)
                    for item in data_list:
                        running = self.process(item)
        except ConnectionResetError:
            print('Connection Reset')

    def send_heartbeats(self):
        t = time.time()
        while True:
            n = time.time()
            if n - t >= JPCProtocol.HEARTBEAT_INTERVAL:
                t = n
                self.send_heartbeat()

    def process(self, data):
        print(data)
        opcode = data['opcode']
        payload = data['payload']

        switcher = {
            JPCProtocol.TELL:       self.process_tell,
            JPCProtocol.ERROR:      self.process_error,
            JPCProtocol.HEARTBEAT:   self.process_heartbeat
        }

        return switcher[opcode](payload)

    def process_tell(self, payload):
        message = payload['message']
        self.gui.set_message(message)
        return True

    def process_error(self, error_code):
        if error_code == JPCProtocol.ERROR_TIMED_OUT:
            self.close()
            return False
        return True

    def process_heartbeat(self, payload):
        return True

    def send(self, msg):
        JPCProtocol(JPCProtocol.SEND, msg).send(self.server)

    def receive(self):
        recv_data = self.server.recv(10000000)
        return recv_data

    def close(self):
        self.server.close()

    def send_heartbeat(self):
        JPCProtocol(JPCProtocol.HEARTBEAT).send(self.server)

