#!/usr/bin/python
import discord
import asyncio
import sys
import socket
import _thread as thread
import math
from collections import deque
from textwrap import wrap

# Discord token here
TOKEN = ""
# List of channel IDs to relay here
CHANNELIDS = [""]

dready = False 

petcolors = {
    'white': bytes([5]),
    'red': bytes([28]),
    'green': bytes([30]),
    'blue': bytes([31]),
    'orange': bytes([129]),
    'black': bytes([144]),
    'brown': bytes([149]),
    'lt red': bytes([150]),
    'dk grey': bytes([151]),
    'dk gray': bytes([151]),
    'md grey': bytes([152]),
    'md gray': bytes([152]),
    'lt green': bytes([153]),
    'lt blue': bytes([154]),
    'lt grey': bytes([155]),
    'lt gray': bytes([155]),
    'purple': bytes([156]),
    'yellow': bytes([158]),
    'cyan': bytes([159])
}

pctuples = {
    (0, 0, 0): 'black',
    (255, 255, 255): 'white',
    (136, 0, 0): 'red',
    (170, 255, 238): 'cyan',
    (204, 68, 204): 'purple',
    (0, 204, 85): 'green',
    (0, 0, 170): 'blue',
    (238, 238, 119): 'yellow',
    (221, 136, 5): 'orange',
    (102, 68, 0): 'brown',
    (255, 119, 119): 'lt red',
    (51, 51, 51): 'dk grey',
    (119, 119, 119): 'md grey',
    (170, 255, 102): 'lt green',
    (0, 136, 255): 'lt blue',
    (187, 187, 187): 'lt gray'
}

dclient = discord.Client()

def colordistance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
    
    
def colormap(point):
    if point == discord.Colour.default():
        return petcolors.get('lt grey')
    else:
        point = point.to_tuple()
        posscolors = list(pctuples.keys())
        closecolors = sorted(posscolors, key=lambda color: colordistance(color, point))
        closestcolor = closecolors[0]
        return petcolors.get(pctuples[closestcolor])
        

def petify(nick, color, msg):
    if len(nick) > 10:
        nick = nick[:7] + "..."
    color = colormap(color)
    if (len(msg) + len(nick) + 4) > 40:
        msglines = wrap(msg, 36-len(nick))
    else:
        msglines = [msg]
    nick = nick.encode("ascii","ignore")
    pnick = b""
    out = []
    for char in nick:
        pnick = pnick + ascpet(char)
    for idx, line in enumerate(msglines):
        line = line.encode("ascii","ignore")
        pmsg = b""
        for char in line:
            pmsg = pmsg + ascpet(char)
        if idx == 0:
            mybuffer = petcolors.get('md gray') + b"<" + color + pnick + petcolors.get('md gray') + b"> " + petcolors.get('white') + pmsg + b'\r'
        else:
            mybuffer = petcolors.get('white') + b" "*(len(nick) + 3) + pmsg + b'\r'
        out.append(mybuffer)
    return out
    

    
            
        
    
@dclient.event
async def on_ready():
    global dready
    print("Discord thread logged in..")
    dready = True

@dclient.event
async def on_message(message):
    origin = message.author
    if message.author.nick is not None:
        nick = message.author.nick
    elif message.author.display_name is not None:
        nick = message.author.display_name
    else:
        nick = message.author.name
    dest = message.channel
    color = message.author.color
    if (dest.is_private == True) or (dest.id not in CHANNELIDS) or (len(tclients) == 0) or (message.author == dclient.user):
        return
    msg = message.content
    petmsg = petify(nick, color, msg)
    for idx,c in enumerate(tclients):
        for line in petmsg:
            try: 
                c.send(line)
            except OSError:
                print("A client has disconnected.")
                del tclients[idx]
                return
                
                
async def check_input_buffers():
    await dclient.wait_until_ready()
    await asyncio.sleep(1)
    while dready == False:
        await asyncio.sleep(1)
    while not dclient.is_closed:
        if len(dbuf) > 0:
            nextline = dbuf.popleft()
            for chid in CHANNELIDS:
                channel = dclient.get_channel(chid)
                if channel is not None:
                    await dclient.send_message(channel, nextline)
        await asyncio.sleep(1)
            
def ascpet(char):
    try:
        val = ord(char)
    except TypeError:
        val = char
    if (val >= 65) and (val <= 90):
        val = val + 128 # Upper case characters
    elif (val >= 97) and (val <= 122):
        val = val - 32 # Lower case characters
    # Anything else should go through unmodified, as it's either the same in ASCII, or unrepresented on PETSCII (poor backslash)
    return bytes([val])

    
def petasc(char):
    specials = {
        3: b"{RUN/STOP}",
        5: b"{WHITE}",
        8: b"{SHIFT DISABLE}",
        14: b"{LOWERCASE/TEXT MODE}",
        17: b"{CURSOR DOWN}",
        18: b"{REVERSE ON}",
        19: b"{HOME}",
        20: b"{DEL}",
        28: b"{RED}",
        29: b"{CURSOR RIGHT}",
        30: b"{GREEN}",
        31: b"{BLUE}",
        129: b"{ORANGE}",
        133: b"{F1}",
        134: b"{F3}",
        135: b"{F5}",
        136: b"{F7}",
        137: b"{F2}",
        138: b"{F4}",
        139: b"{F6}",
        140: b"{F8}",
        141: b'\r',
        142: b"{UPPERCASE/'GRAPHICS' MODE}",
        144: b"{BLACK}",
        145: b"{CURSOR UP}",
        146: b"{REVERSE OFF}",
        147: b"{CLR}",
        148: b"{INSERT}",
        149: b"{BROWN}", #What can it do for you?
        150: b"{LT RED}",
        151: b"{DK GREY}",
        152: b"{MD GREY}",
        153: b"{LT GREEN}",
        154: b"{LT BLUE}",
        155: b"{LT GREY}",
        156: b"{PURPLE}",
        157: b"{CURSOR LEFT}",
        158: b"{YELLOW}",
        159: b"{CYAN}",
        160: b" "
    }
    try:
        val = ord(char)
    except TypeError:
        val = char
    if (val >= 65) and (val <= 90):
        val = val + 32 # Lower case characters
    elif (val >= 193) and (val <= 218):
        val = val - 128 # Upper case characters
    elif (val >= 97) and (val <= 122):
        val = val - 32 # Also upper case characters.
    elif val in specials:
        return specials.get(val) # Special control characters. 
    # Anything else is either a graphical character we can't handle anyway or identical to ascii, so don't do anything with it.
    
    # Return the byte we've fucked about with.
    return bytes([val])
            
        
def doclient(mysocket, addr, num):
        ibuf = b""
        while True:
            try: 
                inchr = mysocket.recv(1)
                # Gray-colored echoback. Wastes quite a bit of bandwidth...
                mysocket.send(b'\x9b' + inchr + b'\x05')
                inchr = petasc(inchr)
            except ConnectionAbortedError:
                break
            except socket.error:
                break
            ibuf = ibuf + inchr
            if inchr == b'\r':
                if dready == True:
                    dbuf.append("<C64#" + cnum + "> " + ibuf.decode("ascii","ignore"))
                ibuf = b""
                
dbuf = deque([])
tclients = []

s = socket.socket()
host = socket.gethostname()
port = 2032
    
print("Starting discord thread...")
dclient.loop.create_task(check_input_buffers())
thread.start_new_thread(dclient.run,(TOKEN,))

print("Starting terminal server thread...")
print("Awaiting terminal client...")
s.bind((host,port))
s.listen(5)

while True:
    c, addr = s.accept()
    tclients.append(c)
    cnum = str(len(tclients))
    print("Accepted client #" + cnum + " from address " + str(addr))
    thread.start_new_thread(doclient,(c,addr,cnum))
s.close()