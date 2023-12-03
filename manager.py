import time


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


def calculate_next_green_time(index, vehicles, vehicles_count, direction_numbers, signals):

    stop_times = {}

    # if average of stop time in a direction is over x, open this direction
    for direction in direction_numbers.values():
        if direction_numbers[index] != direction:
            stop_times[direction] = (calculate_current_avg_wait(vehicles, vehicles_count, direction))

    if len(stop_times) > 0:
        for direction, stop_time in stop_times.items():
            if stop_time > 5:
                i = direction_index_by_name(direction, direction_numbers)
                return i, calculate_green_time(vehicles_count[direction])

    most_populated_index = -1
    most_populated_direction = ""
    aux_1 = 0
    aux_2 = -1
    times = {}

    for _dir, count in vehicles_count.items():
        if count > aux_1:
            aux_1 = count
            times = {_dir: count}
        elif count == aux_1 and count != 0:
            times[_dir] = count

    if len(times) > 1:
        for _dir, count in times.items():
            if calculate_last_green(_dir, direction_numbers, signals) > aux_2:
                aux_2 = calculate_last_green(_dir, direction_numbers, signals)
                most_populated_index = direction_index_by_name(_dir, direction_numbers)
                most_populated_direction = _dir
    else:
        most_populated_index = direction_index_by_name(list(times.keys())[0], direction_numbers)
        most_populated_direction = list(times.keys())[0]

    time_open = calculate_green_time(vehicles_count[most_populated_direction])
    if time_open > 20:
        time_open = 5
    elif time_open < 4:
        time_open = 2

    return most_populated_index, time_open


def calculate_green_time(vehicles_count):
    return vehicles_count * 0.5


def calculate_last_green(direction, direction_numbers, signals):
    index = direction_index_by_name(direction, direction_numbers)

    last_time_was_green = signals[index].lastGreen

    if last_time_was_green != 0:
        return time.time() - last_time_was_green
    else:
        return -1


def calculate_current_avg_wait(vehicles, vehicles_count, direction):
    total_wait = 0
    if vehicles_count[direction] == 0:
        return 0
    else:
        for lane in range(0, 2):
            for vehicle in vehicles[direction][lane]:
                if vehicle.crossed != 1 and vehicle.stopTime != 0:
                    total_wait += time.time() - vehicle.stopTime
                else:
                    total_wait += 0

        return round(total_wait / vehicles_count[direction], 1)


def direction_index_by_name(direction, direction_numbers):
    for index, _dir in direction_numbers.items():
        if _dir == direction:
            return index
