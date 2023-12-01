# Description: This file contains the logic for the traffic light manager
def calculate_next_green(vehicles_count, direction_numbers):
    # Returns the direction and sets the time of the next green signal
    # Called when the time of the currentGreen is 0
    # Will need to have many more metrics to evaluate the next green signal TODO

    num_vehicles_in_most_populated_direction = max(vehicles_count.values())
    aux = ""
    for direction, count in vehicles_count.items():
        if count == num_vehicles_in_most_populated_direction:
            aux = direction

    for index, dicDirection in direction_numbers.items():
        if aux == dicDirection:
            return index


def calculate_next_green_time(index, vehicles_count, direction_numbers):

    num_vehicles_in_most_populated_direction = max(vehicles_count.values())
    aux = ""
    for direction, count in vehicles_count.items():
        if count == num_vehicles_in_most_populated_direction:
            aux = direction

    index_with_most_vehicles = calculate_next_green(vehicles_count, direction_numbers)

    if vehicles_count[aux] == 0:
        return index, 1

    time_open = vehicles_count[aux] * 0.5
    if time_open > 20:
        time_open = 5
    elif time_open < 4:
        time_open = 2

    return index_with_most_vehicles, time_open



# def calculateLastGreen(directionIndex):
#     lastTimeGreen = signals[directionIndex].lastGreen
#     if (lastTimeGreen != 0 and lastTimeGreen != None):
#         lastTimeGreen = time.time() - signals[directionIndex].lastGreen
#         return round(lastTimeGreen, 1)
#     else:
#         # Indicates that the signal is yet to have a time where it was green
#         return -1
