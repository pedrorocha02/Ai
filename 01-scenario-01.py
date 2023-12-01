import random
import time
import threading
import pygame
import sys

# Number of vehicles to be generated
num_vehicles = 100
crossed_vehicle_count = 0

# Default values of signal timers
defaultGreen = {0: 2, 1: 2, 2: 2, 3: 2}
defaultRed = 50
defaultYellow = 2

# Stores the properties of the 4 signals
signals = []
noOfSignals = 4
currentGreen = 0  # Indicates which signal is green currently (0 to (noOfSignals - 1) = 3)
nextGreen = (currentGreen + 1) % noOfSignals  # Indicates which signal will turn green next
currentYellow = 0  # Indicates whether yellow signal is on or off

# Average speeds of the different vehicles (x and y speed)
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}

# Coordinates of vehicles' start depending on its lane
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}

# The type of vehicles present in the game (Can add more in the future)
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}

# All the directions available (Although the vehicles don't change lanes/direction)
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Count of vehicles in each lane
vehiclesCount = {'right': 0, 'down': 0, 'left': 0, 'up': 0}

# Coordinates of signal image, timer, and vehicle count
signalCoords = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoords = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Coordinates of stop lines (y - (up, down) and x - (right, left))
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
# stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

# Gap between vehicles
stoppingGap = 15  # stopping gap
movingGap = 15  # moving gap

# Exit list file
exitListFile = open('./output/_output.csv', 'w')
sys.stdout = exitListFile
exitListFile.write("Direction;Lane;Vehicle class;Index;AvgWait\n")

for direction in directionNumbers.values():
    open(f'./output/{direction}.csv', 'w')

# Initialize the game
pygame.init()
simulation = pygame.sprite.Group()

# List to store wait times for vehicles
wait_times_per_direction = {"right": [], "down": [], "left": [], "up": []}


class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.exitTime = ""
        self.stopTime = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)

        if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][
            self.index - 1].crossed == 0):  # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
            if (direction == 'right'):
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].image.get_rect().width - stoppingGap  # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            elif (direction == 'left'):
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].image.get_rect().width + stoppingGap
            elif (direction == 'down'):
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].image.get_rect().height - stoppingGap
            elif (direction == 'up'):
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]

        # Set new starting and stopping coordinate
        if (direction == 'right'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif (direction == 'left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif (direction == 'down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif (direction == 'up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # How a car moves depending on its direction
    def move(self):
        if (self.direction == 'right'):

            # if the image has crossed stop line now
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.cross()

            # (if the image has not reached its stop coordinate or has crossed stop line or has green signal)
            # and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
            if ((self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (
                    currentGreen == 0 and currentYellow == 0)) and (
                    self.index == 0 or self.x + self.image.get_rect().width < (
                    vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                self.x += self.speed  # move the vehicle
            else:
                if self.stopTime == 0:
                    self.stopTime = time.time()

        elif self.direction == 'down':

            if (self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]):
                self.cross()

            if ((self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
                    currentGreen == 1 and currentYellow == 0)) and (
                    self.index == 0 or self.y + self.image.get_rect().height < (
                    vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                self.y += self.speed
            else:
                if self.stopTime == 0:
                    self.stopTime = time.time()

        elif self.direction == 'left':

            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.cross()

            if ((self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and (
                    self.index == 0 or self.x > (
                    vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                self.index - 1].image.get_rect().width + movingGap))):
                self.x -= self.speed
            else:
                if self.stopTime == 0:
                    self.stopTime = time.time()

        elif self.direction == 'up':

            if (self.crossed == 0 and self.y < stopLines[self.direction]):
                self.cross()

            if ((self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and (
                    self.index == 0 or self.y > (
                    vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][
                self.index - 1].image.get_rect().height + movingGap))):
                self.y -= self.speed
            else:
                if self.stopTime == 0:
                    self.stopTime = time.time()

    def cross(self):
        self.crossed = 1
        self.exitTime = time.time()
        wait_time = 0 if self.stopTime == 0 else round(self.exitTime - self.stopTime, 1)
        vehiclesCount[self.direction] -= 1

        global crossed_vehicle_count
        crossed_vehicle_count += 1

        wait_times_per_direction[self.direction].append(wait_time)

        with open(f'output/{self.direction}.csv', 'a') as f:
            f.write(f"{wait_time}\n")

        with open(f'output/_output.csv', 'a'):
            print(
                f'{self.direction};{self.lane};{self.vehicleClass};{self.index};{wait_time}')


# Begin the values of the game: TraficSignals,
# Initialization of the 4 signals with default values
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
    signals.append(ts4)
    repeat()


def repeat():
    global currentGreen, currentYellow, nextGreen
    while (signals[currentGreen].green > 0):  # while the timer of current green signal is not zero
        updateValues(currentGreen)
        time.sleep(1)
    currentYellow = 1  # set yellow signal on
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while (signals[currentGreen].yellow > 0):  # while the timer of current yellow signal is not zero
        updateValues(currentGreen)
        time.sleep(1)
    currentYellow = 0  # set yellow signal off

    # reset all signal times of current signal to default times
    signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen  # set next signal as green signal
    nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
    signals[nextGreen].red = signals[currentGreen].yellow + signals[
        currentGreen].green  # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()


# Update values of the signal timers after every second
def updateValues(currentGreen):
    for i in range(0, noOfSignals):
        if (i == currentGreen):
            if (currentYellow == 0):
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


# Generating vehicles in the simulation
def generate_vehicles(num=None):
    if num == 0:
        return

    if num is None:
        num = num_vehicles

    n = num

    temp = random.randint(0, 99)
    direction_number = 0
    dist = [25, 50, 75, 100]

    if temp < dist[0]:
        direction_number = 0
    elif temp < dist[1]:
        direction_number = 1
    elif temp < dist[2]:
        direction_number = 2
    elif temp < dist[3]:
        direction_number = 3

    vehicle_type = random.randint(0, 3)
    lane_number = random.randint(1, 2)

    Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])

    vehiclesCount[directionNumbers[direction_number]] += 1

    time.sleep(1)

    n -= 1

    generate_vehicles(n)


class Main:
    thread1 = threading.Thread(name="initialization", target=initialize,
                               args=())  # initialization with the main game components
    thread1.daemon = True
    thread1.start()

    # Colours (RGB Code)
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize (Matches the intersection image)
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("Scenario 1 - Original simulation, fixed times for lights")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    # Thread for generating vehicles that executes in another thread by its self
    # Generating vehicles after loading the other game components
    thread2 = threading.Thread(name="generateVehicles", target=generate_vehicles, args=())
    thread2.daemon = True
    thread2.start()

    # TODO: Add a more gracious way to exit the simulation
    while crossed_vehicle_count < num_vehicles:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))  # display background in simulation

        # display signal and set timer according to current status: green, yellow, or red
        for i in range(0, noOfSignals):
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoords[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoords[i])
            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoords[i])
        signalTexts = ["", "", "", ""]

        # display signal timer
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoords[i])

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()


Main()
