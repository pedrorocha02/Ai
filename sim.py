import random
import threading
import pygame
import sys
import time
import math

from TrafficSignal import TrafficSignal

original_stdout = sys.stdout

# Number of vehicles to be generated
numVehicles = 20

# Default values of signal timers
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}  # The values need to be updated by a function
defaultRed = 150
defaultYellow = 5

# Stores the properties of the 4 signals
no_of_signals = 4
signals = []
for i in range(no_of_signals):
    signals.append(TrafficSignal(defaultRed, defaultYellow, defaultGreen[i], None))

current_green_index = 0  # 0: right; 1: down; 2: left; 3: up
next_green_index = 0

is_yellow_on = False

# Average speeds of the different vehicles (x and y speed)
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}

# Coordinates of vehicles' start depending on its lane
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}

# The type of vehicles present in the game (Can add more in the future)
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}

# All the directions available (Altough the vehicles don't change lanes/direction)
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

vehiclesCount = {'right': 0, 'down': 0, 'left': 0, 'up': 0}  # Count of vehicles in each lane

# Coordinates of signal image, timer, and vehicle count
signalCoords = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoords = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Coordinates of stop lines (y - (up, down) and x - (right, left))
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stoppingGap = 15  # stopping gap
movingGap = 15  # moving gap

# Exit list file
exitListFile = open('output.csv', 'w')
sys.stdout = exitListFile
exitListFile.write("Direction;Lane;Vehicle class;Index;AvgWait;TimeStamp\n")

# for file in directionNumbers.values():
#     with open(f'./output/{file}Wait.csv', 'w') as f:
#         f.write("Index;Vehicle class;Lane;AvgWait;TimeStamp\n")

# Initialize the game
pygame.init()
simulation = pygame.sprite.Group()


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicle_class, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicle_class
        self.speed = speeds[vehicle_class]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.creationTime = time.time()
        self.exitTime = ""
        self.stopTime = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.image = pygame.image.load("images/" + direction + "/" + vehicle_class + ".png")

        # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
            # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap

            previous_vehicle = vehicles[direction][lane][self.index - 1]
            previous_vehicle_size = previous_vehicle.image.get_rect().width
            axis = stoppingGap if direction == 'right' or direction == 'down' else (stoppingGap * -1)

            self.stop = previous_vehicle.stop - previous_vehicle_size + axis
        else:
            self.stop = defaultStop[direction]

        if direction == 'right' or direction == 'left':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp if direction == 'left' else (temp * -1)

        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # How a car moves depending on its direction
    def move(self):

        if self.direction == 'right':

            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.cross()

            # (if the image has not reached its stop coordinate or has crossed stop line or has green signal)
            # and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
            if ((self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (
                    current_green_index == 0 and is_yellow_on is False)) and (
                    self.index == 0 or self.x + self.image.get_rect().width < (
                    vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                self.x += self.speed  # move the vehicle
            else:
                if self.stopTime == 0:
                    self.stopTime = time.time()

        elif self.direction == 'down':

            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                self.cross()

            if ((self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
                    current_green_index == 1 and is_yellow_on is False)) and (
                    self.index == 0 or self.y + self.image.get_rect().height < (
                    vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                self.y += self.speed
            else:
                if self.stopTime == 0:
                    self.stopTime = time.time()

        elif self.direction == 'left':

            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.cross()

            if ((self.x >= self.stop or self.crossed == 1 or (current_green_index == 2 and is_yellow_on is False)) and (
                    self.index == 0 or self.x > (
                    vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                self.index - 1].image.get_rect().width + movingGap))):
                self.x -= self.speed
            else:
                if self.stopTime == 0:
                    self.stopTime = time.time()

        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.cross()

            if ((self.y >= self.stop or self.crossed == 1 or (current_green_index == 3 and is_yellow_on is False)) and (
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

        with open(f'./output.csv', 'a') as file:
            print(f'{self.direction};{self.lane};{self.vehicleClass};{self.index};{wait_time};{time.strftime('%H:%M:%S', time.localtime())}')


# Begin the values of the game: TrafficSignals,
# Initialization of the 4 signals with default values
def initialize():
    repeat()


def repeat():
    global current_green_index, is_yellow_on, next_green_index

    # while the timer of current green signal is not zero
    while (signals[current_green_index].green > 0):
        updateValues(current_green_index)
        time.sleep(1)

    # Set last time green signal was in here
    signals[current_green_index].lastGreen = time.time()

    # set yellow signal on
    is_yellow_on = True

    # reset stop coordinates of lanes and vehicles 
    for i in range(0, 3):
        for vehicle in vehicles[directionNumbers[current_green_index]][i]:
            vehicle.stop = defaultStop[directionNumbers[current_green_index]]
    while (signals[current_green_index].yellow > 0):  # while the timer of current yellow signal is not zero
        updateValues(current_green_index)
        time.sleep(1)

    # set yellow signal off
    is_yellow_on = False

    # reset all signal times of current signal to default times
    signals[current_green_index].green = defaultGreen[current_green_index]
    signals[current_green_index].yellow = defaultYellow
    signals[current_green_index].red = defaultRed

    next_green_index = calculateNextGreen() % no_of_signals
    current_green_index = next_green_index  # set next signal as green signal
    # nextGreen = (currentGreen+1)%noOfSignals    # set next green signal

    signals[next_green_index].red = signals[current_green_index].yellow + signals[
        current_green_index].green  # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()


# Update values of the signal timers after every second
def updateValues(currentGreen):
    for i in range(0, no_of_signals):
        if (i == currentGreen):
            if (is_yellow_on == False):
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
        num = numVehicles

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


def calculateTraffic():
    while True:
        # for direction in directionNumbers.values():
        #     calculateWaitList(direction)
        time.sleep(1)


def calculateNextGreen():
    # Returns the direction and sets the time of the next green signal
    # Called when the time of the currentGreen is 0
    # Will need to have many more metrics to evaluate the next green signal TODO

    directionWithMostVehicles = max(vehiclesCount.values())
    aux = ""
    for direction, count in vehiclesCount.items():
        if count == directionWithMostVehicles:
            aux = direction

    for index, dicDirection in directionNumbers.items():
        if aux == dicDirection:
            return index


# Calculate traffic density
def calculateWaitList(direction):
    for index, dicDirection in directionNumbers.items():
        if direction == dicDirection:
            direction_index = index

    # for direction in directionNumbers.values():
    #     with open(f'./output/{direction}Wait.csv', 'a') as f:
    #         f.write(
    #             f"{vehiclesCount[direction]};{calculateCurrentAvgWait(direction)};{calculateLastGreen(direction_index)};{time.strftime('%H:%M:%S', time.localtime())}\n")


def calculateMetricOutput(direction):
    # Calculate average wait time
    directionAvgWait = calculateCurrentAvgWait(direction)

    # Calculate standard deviation
    directionStandardDeviation = calculateCurrentStandardDeviation(direction)

    # for direction in directionNumbers.values():
    #     with open(f'./output/{direction}Wait.csv', 'a') as f:
    #         f.write(
    #             f"{vehiclesCount[direction]};{directionAvgWait};{directionStandardDeviation};{time.strftime('%H:%M:%S', time.localtime())}\n")


def calculateLastGreen(directionIndex):
    lastTimeGreen = signals[directionIndex].lastGreen
    if (lastTimeGreen != 0 and lastTimeGreen != None):
        lastTimeGreen = time.time() - signals[directionIndex].lastGreen
        return round(lastTimeGreen, 1)
    else:
        # Indicates that the signal is yet to have a time where it was green
        return -1


def calculateCurrentAvgWait(direction):
    totalWait = 0
    if (vehiclesCount[direction] == 0):
        return 0
    else:
        for lane in range(0, 2):
            for vehicle in vehicles[direction][lane]:
                if (vehicle.crossed != 1 and vehicle.stopTime != ""):
                    totalWait += time.time() - vehicle.stopTime
                else:
                    totalWait += 0
        return round(totalWait / vehiclesCount[direction], 1)


def calculateCurrentStandardDeviation(direction):
    directionAvgWait = calculateCurrentAvgWait(direction)

    # List to store wait times for vehicles
    wait_times = []

    for lane in range(0, 2):
        for vehicle in vehicles[direction][lane]:
            if vehicle.crossed != 1 and vehicle.stopTime != "":
                currentWaitTime = time.time() - vehicle.creationTime
                wait_times.append(currentWaitTime)

    # Calculate standard deviation
    if len(wait_times) > 1:
        deviation = round(math.sqrt(sum((x - directionAvgWait) ** 2 for x in wait_times) / (len(wait_times) - 1)), 1)
    else:
        deviation = 0

    return deviation


class Main:
    # Screensize (Matches the intersection image)
    screenSize = (1400, 800)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("MEI - AI")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    threads = [{'name': "initialization", 'target': initialize, 'args': ()},
               {'name': "generateVehicles", 'target': generate_vehicles, 'args': ()},
               {'name': "calculateTraffic", 'target': calculateTraffic, 'args': ()}]

    for thread in threads:
        thread = threading.Thread(name=thread['name'], target=thread['target'], args=thread['args'])
        thread.daemon = True
        thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))  # display background in simulation

        # display signal and set timer according to current status: green, yellow, or red
        for i in range(0, no_of_signals):
            if i == current_green_index:
                if is_yellow_on:
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
        for i in range(0, no_of_signals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, (255, 255, 255), (0, 0, 0))
            screen.blit(signalTexts[i], signalTimerCoords[i])

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()

        pygame.display.update()


Main()
