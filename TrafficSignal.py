class TrafficSignal:
    def __init__(self, red, yellow, green, last_green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
        self.lastGreen = last_green
