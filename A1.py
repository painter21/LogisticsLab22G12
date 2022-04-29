import math

# global variables
transport_demand = []
layout = []
distances = []
robot_list = []


# support functions, many of those were created at some point, no all solutions make use of them
def read_and_transform_to_array(file_name):
    column_list = []

    file = open(file_name)
    # ignore first line
    file.readline().strip()
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
def calc_distances():
    locations = [1, 2, 3, 4, 5, 6]
    global distances
    for loc_a in locations:
        for loc_b in locations:
            distances.append(score_calc(loc_a, loc_b))
def get_distance(loc_1, loc_2):
    # alternative version of score calc where the results are copied from an array.
    # used because in code the following line looks ugly
    return distances[(loc_1-1) * 6 + loc_2 - 1]
def get_remaining_packages(current_transport_demand):
    counter = 0
    for row in current_transport_demand:
        counter += row[2]
    return counter
def write_schedule_txt():
    schedule = open("schedule.txt", "w")
    schedule.write("VehicleId;Location;unload;load" + "\n")
    for robot in robot_list:
        for schedule_entry in robot.schedule_list:
            schedule.write(schedule_entry + "\n")
        if robot.loaded:
            schedule.write(
                str(robot.vehicle_id) + ";" + str(robot.location) + ";1;0")
    schedule.close()
def score_calc(loc_1, loc_2):
    # finding the variables, dirty, but it is working

    # this is just for python, it is scared the following might not define the variables
    loc_1_x, loc_2_x, loc_1_y, loc_2_y = 0, 0, 0, 0

    for location in layout:
        if location[0] == loc_1:
            loc_1_x = location[1]
            loc_1_y = location[2]
        if location[0] == loc_2:
            loc_2_x = location[1]
            loc_2_y = location[2]
    return math.sqrt((loc_1_x - loc_2_x) * (loc_1_x - loc_2_x) + (loc_1_y - loc_2_y) * (loc_1_y - loc_2_y))
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

    # create a list of amount of packages at each station
    count_location_stacks = [0, 0, 0, 0, 0, 0]
    for row in transport_demand:
        count_location_stacks[row[0] - 1] += row[2]

    best_stack = -1
    destination = 0
    remember_row = []
    for row in transport_demand:
        if row[0] == location:
            if best_stack < count_location_stacks[row[1] - 1]:
                best_stack = count_location_stacks[row[1] - 1]
                destination = row[1]
                remember_row = row
    if not remember_row:
        return 0
    remember_row[2] -= 1
    if remember_row[2] == 0:
        transport_demand.remove(remember_row)
    return destination
def get_any_station_with_package():
    return transport_demand[0][0]
def get_next_closest_location_with_package(current_location):
    # with multiple robots, multiple robots could try to catch the same package. We have to get creative:
    ignore_list = [0, 0, 0, 0, 0, 0]
    for robot in robot_list:
        ignore_list[robot.location - 1] += 1

    closest_location = 0
    best_distance = 1000
    last_checked_location = 0
    for row in transport_demand:
        location = row[0]
        if ignore_list[location - 1] > 0:
            ignore_list[location - 1] -= 1
        else:
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
def remove_package_in_transport_demand(start, end):
    global transport_demand
    for row in transport_demand:
        if row[0] == start and row[1] == end:
            if row[2] - 1:
                row[2] -= 1
            else:
                transport_demand.remove(row)
            return 1
    return 0
def run_path(path, vehicle_id=1):
    # this function moves the robot and handles all changes while working a given, otherwise calculated, path
    # since paths are build recursively, we need to work them recursively, so we start with the last element
    # range(x) starts with 0, 1, 2,...., but for array[-i] to work we need to start with 1, so:
    for i in range(len(path)):
        move_robot(path[-(i+1)], vehicle_id)
        # uhm, jup, we are done here
def move_robot(new_location, robot_id=1):
    # whenever the roboter moves, we need to do 4 things:
    # (3) update the position and load, (4) remove the_transport demand in case we load something,
    # (1) update the schedule and (2) update the score
    # since this is always the case, this function will hopefully simplify it.

    # find our robot by id (yes we could just give the robot directly, but this works too, shut up)
    robot = robot_list[robot_id-1]

    # (4), (3) is there a package to deliver from current to new_location, if yes, we always take it
    load = remove_package_in_transport_demand(robot.location, new_location)

    # (1) update the schedule
    robot.schedule_list.append(
        str(robot.vehicle_id) + ";" + str(robot.location) + ";" + str(robot.loaded) + ";" + str(load))

    # (2) update the score, score_calc(robot.location, new_location) would work too, but I saved it in an array
    robot.score += get_distance(robot.location, new_location)

    # (3) update the position and load
    robot.loaded = load
    robot.location = new_location

# algorithms for pathfinding if they are too big for the main solution function
def find_path(location, path_length):
    # recursive start function
    # tries to find the longest path without leaving a note without cargo,
    # is faster than expected, path_length can be infinite for our sample
    # easy to misunderstand: This function just returns a path,
    # it does not send the robot immediately (no schedule creation,
    # removing packages from transport_demand, score calculation. Use run_path for that)

    def find_path_recursive(
            recursive_instance_location, recursive_instance_path_length, recursive_instance_transport_demand):
        # brute force depth search
        # end condition
        if not recursive_instance_path_length:
            return []

        longest_path = []

        # shuffling through all options for packages from current location
        for row in recursive_instance_transport_demand:
            if row[0] == recursive_instance_location:

                # found a fitting next location
                # creating a new theoretical transport_demand list for the next recursive step
                tmp_transport_demand_copy = recursive_instance_transport_demand.copy()
                tmp_transport_demand_copy.remove(row)
                if row[2] - 1:
                    # print(recursive_instance_path_length, [row[0], row[1], row[2] - 1])
                    tmp_transport_demand_copy.append([row[0], row[1], row[2] - 1])
                # else:
                    # print(row[1], recursive_instance_path_length)

                # finding the longest possible path if next location is given
                long_path = \
                    find_path_recursive(row[1], recursive_instance_path_length - 1, tmp_transport_demand_copy)
                # adding the next step
                long_path.append(row[1])

                # is the found path already long enough for the given threshold / good enough
                if len(long_path) == recursive_instance_path_length:
                    return long_path
                else:
                    # is the found path longer then previous paths?
                    if len(longest_path) < len(long_path):
                        longest_path = long_path
        return longest_path

    path = find_path_recursive(location, path_length, transport_demand.copy())
    print("finding path: path length = ", len(path))

    # if there is no package at the current location, and we do not have a path yet, return next best station
    # this way we can force this function until the end
    if not path:
        print(location, [get_next_closest_location_with_package(location)], "no_package")
        return [get_next_closest_location_with_package(location)]

    print(location, path)
    return path
def bruteforce_recursive(location, current_transport_demand, recursion_depth=0):
    # end-condition
    if not len(current_transport_demand):
        return [[], 0]

    # When there are any transports from the current location, we will ignore empty connections
    best_score = 100000
    best_path = []
    not_tested_locations = [1, 2, 3, 4, 5, 6]

    # we need to know if we had any direct transport, I can not think of a proper variable name:
    not_tested_yet = 1

    # this is just for python, it is scared the variable might not be defined:
    tmp_transport_demand_copy = 0

    for row in current_transport_demand:
        if row[0] == location:
            # we found a direct transport, removing it from the transport demand pool
            not_tested_locations.remove(row[1])
            tmp_transport_demand_copy = current_transport_demand.copy()
            tmp_transport_demand_copy.remove(row)
            if row[2]-1:
                tmp_transport_demand_copy.append([row[0], row[1], row[2]-1])

            # recursion
            tmp = bruteforce_recursive(row[1], tmp_transport_demand_copy, recursion_depth + 1)
            # add current location to path
            tmp[0].append(row[1])
            not_tested_yet = 0

            # is this actually the best variant? Adding score malus for planned transport step
            if best_score > tmp[1] + get_distance(location, row[1]):
                best_score = tmp[1] + get_distance(location, row[1])
                best_path = tmp[0]

    # in case we did not find any direct path:
    if not_tested_yet:
        for new_location in not_tested_locations:
            # the new location must have a package
            has_package = 0
            for row in current_transport_demand:
                if new_location == row[0]:
                    has_package = 1
            if has_package:
                # recursion
                tmp = bruteforce_recursive(new_location, current_transport_demand, recursion_depth + 1)
                # add current location to path
                tmp[0].append(new_location)

                # is this actually the best variant? Adding score malus for planned transport step
                if best_score > tmp[1] + get_distance(location, new_location):
                    best_score = tmp[1] + get_distance(location, new_location)
                    best_path = tmp[0]
    return [best_path, best_score]

# solutions for 1 robot
def simple_solution():
    """
    this is a test if the code and validation are working.
    The robot checks if there are any packages to deliver in the current station and grabs them in numeric order. If not
    how goes empty-handed to the next station in numeric order.
    """
    global task_state

    # roboter_state:
    location = 1
    loaded = 0
    vehicle_id = 1
    score = 0

    # solution:
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
    The robot checks if there are any packages to deliver in the current station and grabs them in numeric order. If not
    how goes empty-handed to the NEXT CLOSEST station.
    """
    global task_state

    # roboter_state:
    location = 1
    loaded = 0
    vehicle_id = 1
    score = 0

    # solution:
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
    The robot checks if there are any packages to deliver in the current station and grabs one to the location with
    maximum amount of packages. If not it goes empty-handed to the NEXT CLOSEST station.
    """
    global task_state

    # roboter_state:
    location = 1
    loaded = 0
    vehicle_id = 1
    score = 0

    # solution:
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
def solution_03(max_path_length=5, rest_packages=20):
    """
    The robot tries to avoid empty runs for as long as possible until less than rest_packages packages are left.
    The rest are done via brute Force.
    """
    global transport_demand
    global robot_list

    # state
    robot_list.append(Robot(1))
    robot = robot_list[0]

    # solution:
    schedule = open("schedule.txt", "w")
    schedule.write("VehicleId;Location;unload;load" + "\n")

    while 1:
        # debugging
        print("\nnew while, remaining: ", get_remaining_packages(transport_demand))
        print(transport_demand)

        # is anything left?
        if len(transport_demand) == 0:
            print("solution_01:done")
            write_schedule_txt()
            print("score: ", robot.score)
            return

        # are more than max_packages left?
        if get_remaining_packages(transport_demand) > rest_packages:
            path = find_path(robot.location, max_path_length)
            run_path(path)
            continue

        # there are not:
        path_and_score = bruteforce_recursive(robot.location, transport_demand.copy())
        print("finding brute-force path: path length = ", len(path_and_score[0]))
        print(path_and_score[0])
        run_path(path_and_score[0])


class Robot:
    def __init__(self, location):
        self.location = location
        self.vehicle_id = location
        self.loaded = 0
        self.busy_until = 0

        # schedule list, needs to be written into schedule.txt later, we could just use a long string, but I decided
        # against. It is highly debatable, but it feels easier to modify later if needed
        self.schedule_list = []

        # robot will shut down if it can't find work.
        self.shutdown = 0

        # how long is the robot busy? the lowest score is the next free robot,
        # the highest score from all robots in the end is the final score
        self.score = 0

def multibot_solution_02(robot_count):
    """
    Robots are called in numeric order as soon as they are free.
    The robot checks if there are any packages to deliver in the current station and grabs one to the location with
    maximum amount of packages. If not it goes empty-handed to the NEXT CLOSEST station.

    This is wild, Do not try to understand it
    """
    # state
    global robot_list
    score = 0  # score = time
    for i in range(robot_count):
        robot_list.append(Robot(i + 1))

    while 1:
        # check if done
        all_shutdown = 1
        for robot in robot_list:
            if not robot.shutdown:
                all_shutdown = 0
        if all_shutdown:
            break

        # check for the next robot available
        next_done_time = 10000000
        next_done_robot = robot_list[0]
        for robot in robot_list:
            if not robot.shutdown:
                if robot.busy_until < next_done_time:
                    next_done_time = robot.busy_until
                    next_done_robot = robot
        robot = next_done_robot

        # advance timer/ wait until robot is done
        score = robot.busy_until

        next_location = get_package_by_location_to_most_stacked_location(next_done_robot.location)
        to_load = "1"
        if not next_location:
            # no boxes at current location available any more
            next_location = get_next_closest_location_with_package(robot.location)
            to_load = "0"

        # bug fixing
        print("robot: ", robot.vehicle_id)
        print(transport_demand)
        print("loc: " + str(robot.location) + ",unloaded: " + str(robot.loaded) + ",loaded:" + to_load + ",next:" +
              str(next_location) + "\n")
        if next_location:
            robot.busy_until = score + score_calc(robot.location, next_location)
            robot.schedule_list.append(
                str(robot.vehicle_id) + ";" + str(robot.location) + ";" + str(robot.loaded) + ";" + to_load + "\n"
            )
            robot.location = next_location
            robot.loaded = to_load
        else:
            robot.schedule_list.append(
                str(robot.vehicle_id) + ";" + str(robot.location) + ";" + str(robot.loaded) + ";" + "0" + "\n"
            )
            robot.shutdown = 1
            print("shutdown")

    # only for score:
    for robot in robot_list:
        if score < robot.busy_until:
            score = robot.busy_until

    # write schedule.txt
    schedule = open("schedule.txt", "w")
    schedule.write("VehicleId;Location;unload;load" + "\n")
    for robot in robot_list:
        for line in robot.schedule_list:
            schedule.write(line)
    schedule.close()
    print("\ndone\nScore: ", score)


# init
if 1:
    transport_demand = read_and_transform_to_array('transport_demand.txt')
    layout = read_and_transform_to_array('layout.txt')
    calc_distances()

solution_03(147, 13)
"""list_01 = [1]
list_01.append(1)
print(list_01)
"""
