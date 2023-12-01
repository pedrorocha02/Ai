# Description: This file contains the logic for the traffic light manager
def calculate_next_green(vehicles_count, direction_numbers):
    # Returns the direction and sets the time of the next green signal
    # Called when the time of the currentGreen is 0
    # Will need to have many more metrics to evaluate the next green signal TODO

    direction_with_most_vehicles = max(vehicles_count.values())
    aux = ""
    for direction, count in vehicles_count.items():
        if count == direction_with_most_vehicles:
            aux = direction

    for index, dicDirection in direction_numbers.items():
        if aux == dicDirection:
            return index
