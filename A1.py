import math

#global variables
transport_demand = []
layout = []

# Hilfsfunktionen jeder Art
def read_and_transform_to_array(file_name):
    column_list = []

    file = open(file_name)
    # ingore first line
    tmp = file.readline().strip()
    tmp = file.readline().strip()

    while tmp != "":
        row_list = []
        tmp = str(tmp).split(";")
        for i in tmp:
            row_list.append(int(i))
        column_list.append(row_list)
        tmp = file.readline().strip()

    file.close()
    return column_list
def score_calc(loc_1, loc_2):
    # finden der werte, unelegant, geht aber
    for location in layout:
        if location[0] == loc_1:
            loc_1_x = location[1]
            loc_1_y = location[2]
        if location[0] == loc_2:
            loc_2_x = location[1]
            loc_2_y = location[2]
    return math.sqrt((loc_1_x-loc_2_x)*(loc_1_x-loc_2_x)+(loc_1_y-loc_2_y)*(loc_1_y-loc_2_y))
def get_package_by_location(location):
    global transport_demand

    for row in transport_demand:
        if row[0] == location:
            destination = row[1]
            row[2] -= 1
            if row[2] == 0:
                transport_demand.remove(row)
            return destination
    return 0
def get_package_by_location_to_most_stacked_location(location):
    global transport_demand

    #create a list of amount of packages at each station
    count_location_stacks = [0,0,0,0,0,0]
    for row in transport_demand:
        count_location_stacks[row[0]-1] += row[2]

    best_stack = -1
    destinaton = 0
    remember_row = []
    for row in transport_demand:
        if row[0] == location:
            if best_stack < count_location_stacks[row[1]-1]:
                best_stack = count_location_stacks[row[1]-1]
                destination = row[1]
                remember_row = row
    if remember_row == []:
        return 0
    remember_row[2] -= 1
    if remember_row[2] == 0:
        transport_demand.remove(remember_row)
    return destination
def get_any_station_with_package():
    return transport_demand[0][0]
def get_next_closest_location_with_package(current_location):
    closest_location = 0
    best_distance = 1000
    last_checked_location = 0
    for row in transport_demand:
        location = row[0]
        if last_checked_location != location:
            distance = score_calc(location, current_location)
            if distance < best_distance:
                best_distance = distance
                closest_location = location
            last_checked_location = location
    return closest_location
def min_score_calc():
    score = 0
    for row in transport_demand:
        score += score_calc(row[0], row[1]) * row[2]
    print(score)

# Lösungsfunktionen
def simple_solution():
    """
    this is more a test if the code and validation are working.
    The robot checks if there are any packages to deilver in the current sation and grabs them in numeric order. If not
    how goes empty handed to the next station in numeric order.
    """
    global task_state

    #roboter_state:
    location = 1
    loaded = 0
    vehicle_id = 1
    score = 0

    #solution:
    schedule = open("schedule.txt", "w")
    schedule.write("VehicleId;Location;unload;load" + "\n")

    while 1:
        # is anything left?
        if len(transport_demand) == 0:
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + "1" + ";" + "0")
            print("simple_solution:done")
            print("score: ", score)
            schedule.close()
            return

        # do we have a package at the current location
        destination = get_package_by_location(location)
        if destination:
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + str(loaded) + ";" + "1" + "\n")
            score += score_calc(location, destination)
            location = destination
            loaded = 1

        # where is the next package
        else:
            destination = get_any_station_with_package()
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + str(loaded) + ";" + "0" + "\n")
            score += score_calc(location, destination)
            location = destination
            loaded = 0
def solution_01():
    """
    The robot checks if there are any packages to deilver in the current sation and grabs them in numeric order. If not
    how goes empty handed to the NEXT CLOSEST station.
    """
    global task_state

    #roboter_state:
    location = 1
    loaded = 0
    vehicle_id = 1
    score = 0

    #solution:
    schedule = open("schedule.txt", "w")
    schedule.write("VehicleId;Location;unload;load" + "\n")

    while 1:
        # is anything left?
        if len(transport_demand) == 0:
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + "1" + ";" + "0")
            print("solution_01:done")
            print("score: ", score)
            schedule.close()
            return

        # do we have a package at the current location
        destination = get_package_by_location(location)
        if destination:
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + str(loaded) + ";" + "1" + "\n")
            score += score_calc(location, destination)
            location = destination
            loaded = 1

        # where is the next package
        else:
            destination = get_next_closest_location_with_package(location)
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + str(loaded) + ";" + "0" + "\n")
            score += score_calc(location, destination)
            location = destination
            loaded = 0
def solution_02():
    """
    The robot checks if there are any packages to deilver in the current sation and grabs one to the location with
    maximum amount of packages. If not it goes empty handed to the NEXT CLOSEST station.
    """
    global task_state

    #roboter_state:
    location = 1
    loaded = 0
    vehicle_id = 1
    score = 0

    #solution:
    schedule = open("schedule.txt", "w")
    schedule.write("VehicleId;Location;unload;load" + "\n")

    while 1:
        # is anything left?
        if len(transport_demand) == 0:
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + "1" + ";" + "0")
            print("solution_01:done")
            print("score: ", score)
            schedule.close()
            return

        # do we have a package at the current location
        destination = get_package_by_location_to_most_stacked_location(location)
        if destination:
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + str(loaded) + ";" + "1" + "\n")
            score += score_calc(location, destination)
            location = destination
            loaded = 1

        # where is the next package
        else:
            print(location)
            destination = get_next_closest_location_with_package(location)
            schedule.write(str(vehicle_id) + ";" + str(location) + ";" + str(loaded) + ";" + "0" + "\n")
            score += score_calc(location, destination)
            location = destination
            loaded = 0

class robot:
    def __init__(self, location):
        self.location = location
        self.loaded = 0
        self.busy_until = 0

def multibot_solution_02(robot_count):
    """
    Robots are called in numeric order as soon as they are free.
    The robot checks if there are any packages to deilver in the current sation and grabs one to the location with
    maximum amount of packages. If not it goes empty handed to the NEXT CLOSEST station.
    """
    robot_list = []
    schedule_list = []
    for i in range(robot_count):
        robot_list.append(robot(i+1))
        schedule_list.append([])


transport_demand = read_and_transform_to_array('transport_demand.txt')
layout = read_and_transform_to_array('layout.txt')
multibot_solution_02(3)