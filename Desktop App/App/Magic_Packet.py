#For sending magic packet
import socket
from typing import List
from typing import Optional

#building gui app
import os, sys
from kivy.resources import resource_add_path, resource_find
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.switch import Switch

BROADCAST_IP = "255.255.255.255"
DEFAULT_PORT = 7

#This function checks the MAC address format and create magic packet
def create_magic_packet(macaddress: str, mode: str) -> bytes:

    if len(macaddress) == 17:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, "")
    elif len(macaddress) == 14:
        sep = macaddress[4]
        macaddress = macaddress.replace(sep, "")
    if len(macaddress) != 12:
        raise ValueError("Incorrect MAC address format")
    
    #Magic Packet Structure
    if(mode == 'Normal'):
        return bytes.fromhex("F" * 12 + macaddress * 16 )

    if(mode == 'Latch'):
        return bytes.fromhex("F" * 12 + macaddress * 15 )

#This function sends the magic packet to a specified Host.
def send_magic_packet(
    *macs: str,
    ip_address: str = BROADCAST_IP,
    port: int = DEFAULT_PORT,
    interface: Optional[str] = None,
    mode: str = "Normal"
) -> None:
    if(mode == 'Latch'):
        packets = [create_magic_packet(mac,'Latch') for mac in macs]
    else:
        packets = [create_magic_packet(mac,'Normal') for mac in macs]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        if interface is not None:
            sock.bind((interface, 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.connect((ip_address, port))
        for packet in packets:
            sock.send(packet)

########################################
############### GUI APP ################
########################################

#Size of App windows in px
Window.size = (300, 550)

class WOWLAN(App):
    def build(self):
        #Latch mode is turned off by default
        self.latch_mode="OFF"
        #returns a window object with all it's widgets
        self.window = GridLayout(spacing=20)
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y":0.5}

        # Logo image widget
        self.img = Image(source ='wowlan.png')
        self.img.allow_stretch = True
        self.img.keep_ratio = True
        self.img.size_hint_x = 5
        self.img.size_hint_y = 5
        self.window.add_widget(self.img)

        #Switch function(Latch or Normal)
        def Switch_Func(instance, value):
            if(value):
                self.latch_mode="ON"
            else:
                self.latch_mode="OFF"
        
        self.switch = Switch()
        self.switch.bind(active=Switch_Func)
        self.window.add_widget(self.switch)

        #IP label widget
        self.iplabel = Label(
                        text= "Target IP Address",
                        font_size= 12,
                        color= '#00FFCE',
                        bold=True
                        )
        self.window.add_widget(self.iplabel)

        # IP text input widget
        self.ip = TextInput(
                    multiline= False,
                    font_size=12,
                    padding=2,
                    )

        self.window.add_widget(self.ip)

        # Mac address label widget
        self.maclabel = Label(
                        text= "Target Mac Address",
                        font_size= 12,
                        color= '#00FFCE',
                        bold=True
                        )
        self.window.add_widget(self.maclabel)

        # Mac address text input widget
        self.mac = TextInput(
                    multiline= False,
                    font_size=12,
                    padding=2,
                    text="94:B5:55:2C:D0:F0"
                    )
        self.window.add_widget(self.mac)

        #send packet button widget
        self.button = Button(
                text= "Send Packet",
                bold= True,
                background_color ='#00FFCE',
                #remove darker overlay of background colour
                # background_normal = ""
                )
                
        self.button.bind(on_press=self.Send_Packet)
        self.window.add_widget(self.button)

        #alert label widget
        self.alertlabel = Label(
                        text= "",
                        font_size= 14,
                        color= '#00FFCE',
                        )
        self.window.add_widget(self.alertlabel)

        return self.window

    #This function sends the magic packet to specified ip & mac address
    def Send_Packet(self, instance):
        self.alertlabel.color='00FF00'
        self.alertlabel.text = "Magic Packet sent successfully!"

        #both empty
        if(len(self.mac.text)==0 and len(self.ip.text)==0):
            self.alertlabel.color='FF0000'
            self.alertlabel.text = "Both fields cannot be empty!"

        #both filled
        elif(len(self.mac.text)!=0 and len(self.ip.text)!=0):
            if(self.latch_mode=="ON"):
                send_magic_packet(self.mac.text,ip_address=self.ip.text,port=7,mode='Latch')
            else:
                send_magic_packet(self.mac.text,ip_address=self.ip.text,port=7)

        #empty mac address
        else:
            if(len(self.mac.text)==0):
                self.alertlabel.color='FF0000'
                self.alertlabel.text = "Mac address field cannot be empty!"

        #empty ip address
            if(len(self.ip.text)==0):
                if(self.latch_mode=="ON"):
                    send_magic_packet(self.mac.text,port=7,mode='Latch')
                else:
                    send_magic_packet(self.mac.text,port=7)



# run App Calss
if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    WOWLAN().run()
