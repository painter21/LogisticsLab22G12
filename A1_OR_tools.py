import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# my code
def read_layout_and_transform_to_array():
    column_list = []

    file = open("layout.txt")
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
def score_calc(loc_1, loc_2, layout):
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
    return int(math.sqrt((loc_1_x - loc_2_x) * (loc_1_x - loc_2_x) + (loc_1_y - loc_2_y) * (loc_1_y - loc_2_y)))
def calc_distance_matrix(layout):
    locations = [1, 2, 3, 4, 5, 6, 7, 8]
    my_distance_matrix = []
    for loc_a in locations:
        row = []
        for loc_b in locations:
            row.append(score_calc(loc_a, loc_b, layout))
        my_distance_matrix.append(row)
    return my_distance_matrix


"""Simple Travelling Salesperson Problem (TSP) between cities."""

# sample code
def create_data_model():
    """Stores the data for the problem."""
    data = {}
    print("read layout.txt")
    layout = read_layout_and_transform_to_array()
    print("calc distance matrix")
    distance_matrix = calc_distance_matrix(layout)

    for row in distance_matrix:
        print(row)
    data['distance_matrix'] = distance_matrix # yapf: disable
    data['num_vehicles'] = 4
    data['depot'] = 0
    return data


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    print(plan_output)
    plan_output += 'Route distance: {}miles\n'.format(route_distance)


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(manager, routing, solution)


if __name__ == '__main__':
    main()