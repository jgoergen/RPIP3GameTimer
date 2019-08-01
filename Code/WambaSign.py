import random, math, time, urllib
from subprocess import check_output
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
import SimpleHTTPServer, SocketServer, threading, re

# Settings #############################################################
# put any adjustable settings here that would be interesting to tinker with.

MATRIX_DISPLAY_WIDTH = 64
MATRIX_DISPLAY_HEIGHT = 32

HTTP_SERVER_PORT = random.randint(5000, 9000)

LOOP_REPEAT_SLEEP = 0.03
IP_FLIP_SPEED = 200

TIMER_COUNTDOWN_WARNING_SECONDS_1 = 20
TIMER_COUNTDOWN_WARNING_SECONDS_2 = 10
TIMER_COUNTDOWN_WARNING_SECONDS_3 = 5
TIMER_COUNTDOWN_WARNING_SECONDS_4 = 3

RED_CHANGE_SPEED = 0.5
GREEN_CHANGE_SPEED = 0.9
BLUE_CHANGE_SPEED = 1.2

NEW_SCORE_FIREWORKS_MAX_PARTICLES = 20
NEW_SCORE_FIREWORKS_GRAVITY = 0.4
NEW_SCORE_FIREWORKS_FIRED = 20
NEW_SCORE_FIREWORKS_WIDTH = 4
NEW_SCORE_FIREWORKS_HEIGHT = -4
NEW_SCORE_FIREWORKS_DEADZONE_MIN = -0.2
NEW_SCORE_FIREWORKS_DEADZONE_MAX = 0.2

##########################################################################

print("starting init")

# init matrix

options = RGBMatrixOptions()
options.rows = MATRIX_DISPLAY_HEIGHT
options.cols = MATRIX_DISPLAY_WIDTH
# options.brightness = self.args.led_brightness
matrix = RGBMatrix(options = options)
font = graphics.Font()
font.LoadFont("fonts/7x13.bdf")
font2 = graphics.Font()
font2.LoadFont("fonts/10x20.bdf")
offscreen_canvas = matrix.CreateFrameCanvas()

startMillis = int(round(time.time() * 1000))
elapsed = startMillis
r = 150
rChange = RED_CHANGE_SPEED
g = 150
gChange = GREEN_CHANGE_SPEED
b = 150
bChange = BLUE_CHANGE_SPEED
timerRunning = False
done = False
score1 = 0
score2 = 0
minutesStr = "00"
secondsStr = "00"
millisStr = "000"
connected = False
fireworks = []
timerFunction = 0
timerMaxMillis = 0

# functions #########################################################

def isOnline():
    try:
        urllib.urlopen("https://www.google.com")
        return True
    except:
        return False

def getIP():
    wifiIp = check_output(['hostname', '-I'])
    if wifiIp is not None:
        return wifiIp

def rotateRGB():
    global r
    global rChange
    global g
    global gChange
    global b
    global bChange

    r += rChange
    if r > 255 or r < 0:
        rChange *= -1

    g += gChange
    if g > 255 or g < 0:
        gChange *= -1
        
    b += bChange
    if b > 255 or b < 0:
        bChange *= -1

def updateTime():
    global stopTimer
    global elapsed
    global minutesStr
    global secondsStr
    global millisStr
    global timerFunction
    global timerMaxMillis
    global r
    global g
    global b
    global TIMER_COUNTDOWN_WARNING_SECONDS_1
    global TIMER_COUNTDOWN_WARNING_SECONDS_2
    global TIMER_COUNTDOWN_WARNING_SECONDS_3
    global TIMER_COUNTDOWN_WARNING_SECONDS_4

    # calculate time display
    elapsed = 0

    if timerFunction == 0:
        # counting up
        elapsed = int(round(time.time() * 1000)) - startMillis
    else:
        # counting down
        elapsed = timerMaxMillis - (int(round(time.time() * 1000)) - startMillis)

        # is this a countdown?
        if timerFunction != 0:
            # are we approaching 0?
            if elapsed < (1000 * TIMER_COUNTDOWN_WARNING_SECONDS_4):
                r = 255
                g = b = (math.sin(elapsed / 50) + 1) * 120
            elif elapsed < (1000 * TIMER_COUNTDOWN_WARNING_SECONDS_3):
                r = 225
                g = b = (math.sin(elapsed / 90) + 1) * 100
            elif elapsed < (1000 * TIMER_COUNTDOWN_WARNING_SECONDS_2):
                r = 200
                g = b = (math.sin(elapsed / 120) + 1) * 80
            elif elapsed < (1000 * TIMER_COUNTDOWN_WARNING_SECONDS_1):
                r = 180
                g = b = (math.sin(elapsed / 150) + 1) * 50
            
        # done counting down, stop and bail
        if elapsed < 0:
            minutesStr = "XX"
            secondsStr = "XX"
            millisStr = "XXX"
            stopTimer()
            return

    minutes = int(elapsed / (60 * 1000))
    elapsed -= (minutes * (60 * 1000))
    seconds = int(elapsed / 1000)
    elapsed -= seconds * 1000

    minutesStr = str(minutes)
    if len(minutesStr) < 2: minutesStr = "0" + minutesStr

    secondsStr = str(seconds)
    if len(secondsStr) < 2: secondsStr = "0" + secondsStr

    millisStr = str(elapsed)
    if len(millisStr) < 2: millisStr = "0" + millisStr
    if len(millisStr) < 3: millisStr = "0" + millisStr

def resetTimer():
    global r
    global rChange
    global g
    global gChange
    global b
    global bChange
    global startMillis
    global elapsed
    global minutesStr
    global secondsStr
    global millisStr
    global timerFunction
    global timerMaxMillis

    startMillis = int(round(time.time() * 1000))
    elapsed = startMillis
    r = 150
    rChange = RED_CHANGE_SPEED
    g = 150
    gChange = GREEN_CHANGE_SPEED
    b = 150
    bChange = BLUE_CHANGE_SPEED

    if timerFunction == 0:
        #elapsed, counting up
        timerMaxMillis = 0
        minutesStr = "00"
        secondsStr = "00"
        millisStr = "000"
    
    elif timerFunction == 1:
        # 1 = 30 seconds, counting down
        timerMaxMillis = 1000 * 30
        minutesStr = "00"
        secondsStr = "30"
        millisStr = "000"

    elif timerFunction == 2:
        # 2 = 1 minute, counting down
        timerMaxMillis = 1000 * 60 * 1
        minutesStr = "01"
        secondsStr = "00"
        millisStr = "000"

    elif timerFunction == 3:
        # 3 = 2 minute, counting down
        timerMaxMillis = 1000 * 60 * 2
        minutesStr = "02"
        secondsStr = "00"
        millisStr = "000"

    elif timerFunction == 4:
        # 4 = 3 minute, counting down
        timerMaxMillis = 1000 * 60 * 3
        minutesStr = "03"
        secondsStr = "00"
        millisStr = "000"

    elif timerFunction == 5:
        # 5 = 5 minute, counting down
        timerMaxMillis = 1000 * 60 * 5
        minutesStr = "05"
        secondsStr = "00"
        millisStr = "000"

    elif timerFunction == 6:
        # 6 = 10 minute, counting down
        timerMaxMillis = 1000 * 60 * 10
        minutesStr = "10"
        secondsStr = "00"
        millisStr = "000"

def startTimer():
    global timerRunning
    global startMillis
    global elapsed

    if timerRunning == False:
        startMillis = int(round(time.time() * 1000))
        elapsed = startMillis
        timerRunning = True

def stopTimer():
    global timerRunning
    timerRunning = False

def processFireworks():
    global fireworks
    global offscreen_canvas
    global r
    global rChange
    global g
    global gChange
    global b
    global NEW_SCORE_FIREWORKS_GRAVITY
    global MATRIX_DISPLAY_HEIGHT
    global MATRIX_DISPLAY_WIDTH

    for point in fireworks:
        point['x'] += point['velX']
        point['y'] += point['velY']
        point['velY'] += NEW_SCORE_FIREWORKS_GRAVITY
    
        if (point['x'] < 0 or point['x'] > MATRIX_DISPLAY_WIDTH or point['y'] < 0 or point['y'] > MATRIX_DISPLAY_HEIGHT):
            fireworks.remove(point)
        else:
            offscreen_canvas.SetPixel(
                point['x'], 
                point['y'], 
                random.randint(0, int(b)),
                random.randint(0, int(g)),
                random.randint(0, int(r)))

def addFireworks(side):
    global fireworks
    global score1
    global score2
    global NEW_SCORE_FIREWORKS_MAX_PARTICLES
    global NEW_SCORE_FIREWORKS_FIRED
    global NEW_SCORE_FIREWORKS_WIDTH
    global NEW_SCORE_FIREWORKS_HEIGHT
    global NEW_SCORE_FIREWORKS_DEADZONE_MIN
    global NEW_SCORE_FIREWORKS_DEADZONE_MAX

    for i in range(0, NEW_SCORE_FIREWORKS_FIRED):
        if len(fireworks) < NEW_SCORE_FIREWORKS_MAX_PARTICLES:
            # x can go in either direction
            velX = (random.random() * NEW_SCORE_FIREWORKS_WIDTH) - (NEW_SCORE_FIREWORKS_WIDTH / 2)
            # y can only go upwards
            velY = (random.random() * NEW_SCORE_FIREWORKS_HEIGHT)

            # make sure these aren't spawned with too little velocity to move
            if velX < NEW_SCORE_FIREWORKS_DEADZONE_MAX and velX > NEW_SCORE_FIREWORKS_DEADZONE_MIN:
                velX = NEW_SCORE_FIREWORKS_DEADZONE_MAX
            
            if velY < NEW_SCORE_FIREWORKS_DEADZONE_MAX and velY > NEW_SCORE_FIREWORKS_DEADZONE_MIN:
                velY = NEW_SCORE_FIREWORKS_DEADZONE_MAX

            fireworks.append({
                'x': 12 + (38 if side == 2 else 0),
                'y': 25,
                'velX': velX,
                'velY': velY
            })

def changeTimerFunction(functionMode):
    global timerFunction
    global resetTimer
    global stopTimer

    timerFunction = functionMode
    stopTimer()
    resetTimer()
    print("Timer function set to ", timerFunction)

# init webserver

class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_my_headers()
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

    def send_my_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

    def do_GET(self):
        global startTimer
        global stopTimer
        global resetTimer
        global addFireworks
        global changeTimerFunction
        global score1
        global score2
        global connected

        print("get request " + self.path)

        if None != re.search('/api/settimer0', self.path):
            changeTimerFunction(0)
            self.send_response(200)
            self.end_headers()
            return

        if None != re.search('/api/settimer1', self.path):
            changeTimerFunction(1)
            self.send_response(200)
            self.end_headers()
            return

        if None != re.search('/api/settimer2', self.path):
            changeTimerFunction(2)
            self.send_response(200)
            self.end_headers()
            return

        if None != re.search('/api/settimer3', self.path):
            changeTimerFunction(3)
            self.send_response(200)
            self.end_headers()
            return

        if None != re.search('/api/settimer4', self.path):
            changeTimerFunction(4)
            self.send_response(200)
            self.end_headers()
            return

        if None != re.search('/api/settimer5', self.path):
            changeTimerFunction(5)
            self.send_response(200)
            self.end_headers()
            return

        if None != re.search('/api/settimer6', self.path):
            changeTimerFunction(6)
            self.send_response(200)
            self.end_headers()
            return

        if None != re.search('/api/starttimer', self.path):
            startTimer()
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/stoptimer', self.path):
            stopTimer()
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/resettimer', self.path):
            resetTimer()
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/incscore1', self.path):
            score1 += 1
            addFireworks(1)
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/decscore1', self.path):
            score1 -= 1
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/resetscore1', self.path):
            score1 = 0
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/incscore2', self.path):
            score2 += 1
            addFireworks(2)
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/decscore2', self.path):
            score2 -= 1
            self.send_response(200)
            self.end_headers()
            return

        elif None != re.search('/api/resetscore2', self.path):
            score2 = 0
            self.send_response(200)
            self.end_headers()
            return

        else:
            #serve files, and directory listings by following self.path from
            #current working directory
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
            connected = True

httpd = SocketServer.ThreadingTCPServer(("", HTTP_SERVER_PORT), CustomHandler)
thread = threading.Thread(target = httpd.serve_forever)
thread.daemon = True

try:
    thread.start()
except KeyboardInterrupt:
    server.shutdown()
    sys.exit(0)
    
# loop ############################################################

piOnline = isOnline()
ipAddress = ""
ipDisplayFlip = 0

if piOnline == True:
    ipAddress = getIP()
    ipParts = ipAddress.split(".")

print("Server started on " + str(HTTP_SERVER_PORT))
print("Server IP: " + ipAddress)


while not done:
    # offscreen_canvas.Clear()
    offscreen_canvas.Fill(b / 10, r / 10, g / 10)
    processFireworks()

    if connected is not True:
        
        if piOnline == True:
            ipDisplayFlip += 1

            if ipDisplayFlip > (IP_FLIP_SPEED * 2):
                ipDisplayFlip = 0

            elif ipDisplayFlip > IP_FLIP_SPEED and ipAddress is not None:
                graphics.DrawText(offscreen_canvas, font, 8, 10, graphics.Color(150, 150, 150), ipParts[0] + "." + ipParts[1])
                graphics.DrawText(offscreen_canvas, font, 8, 21, graphics.Color(150, 150, 150), ipParts[2] + "." + ipParts[3])

            else:
                graphics.DrawText(offscreen_canvas, font, 10, 9, graphics.Color(150, 150, 150), "matrix")
                graphics.DrawText(offscreen_canvas, font, 5, 19, graphics.Color(150, 150, 150), "display:")

            graphics.DrawText(offscreen_canvas, font, 19, 31, graphics.Color(150, 150, 250), str(HTTP_SERVER_PORT))

        else:
            graphics.DrawText(offscreen_canvas, font, 10, 9, graphics.Color(150, 150, 150), "Not online")
            graphics.DrawText(offscreen_canvas, font, 30, 19, graphics.Color(150, 150, 150), "=(")

    else:
        rotateRGB()

        if timerRunning:
            updateTime()
        
        graphics.DrawText(
            offscreen_canvas, 
            font, 
            1, 
            10, 
            graphics.Color(r, g, b), 
            minutesStr + ":" + secondsStr + ":" + millisStr)

        graphics.DrawText(
            offscreen_canvas, 
            font2,
            2 + (4 if score1 < 10 else 0), 
            29, 
            graphics.Color(r, g, b), 
            str(score1))

        graphics.DrawText(
            offscreen_canvas, 
            font2, 
            41 + (4 if score2 < 10 else 0), 
            29, 
            graphics.Color(r, g, b), 
            str(score2))

    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    time.sleep(LOOP_REPEAT_SLEEP)

# graphics.DrawText(offscreen_canvas, font, x, y, graphics.Color(0, 0, 255), "Text")
# graphics.DrawCircle(offscreen_canvas, x, y, radius, graphics.Color(0, 0, 255))
# graphics.DrawLine(offscreen_canvas, x, y, x2, y2, graphics.Color(0, 0, 255))
# offscreen_canvas.SetPixel(x, y, r, g, b)