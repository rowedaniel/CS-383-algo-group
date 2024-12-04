# Elliot M, Alex, Ian, Daniel

import copy
import random
import time
from concurrent.futures import ThreadPoolExecutor
from electorate import Electorate

#Uncomment this to make function behavoir deterministic
#random.seed(4)

#Point object which is a coordinate and a color
class Point:
    def __init__(self, row, col,color,size):
        self.id = row + (col * size)
        self.row = row
        self.col = col
        self.color = color
        self.neighbors = 0

    def __str__(self):
        return '\x1b[6;' + str(self.color) + ';40m' + "(" + str(self.row) + " " + str(self.col) + ")" + '\x1b[0m'

# A grid of points with a large set of methods to get different data from points
class Grid:
    #Construct the grid
    def __init__(self, sizeOf):
        grid = []
        for i in range(sizeOf):
            row = []
            for j in range(sizeOf):
                p = Point(i,j,37,sizeOf)
                row.append(p)
            grid.append(row)
        self.grid = grid
        self.size = sizeOf

    #Display the Grid with the respective color from points
    def __str__(self):
        str = ""
        for row in self.grid:
            for point in row:
                str += point.__str__() + '\x1b[6;35;40m' + " " + '\x1b[0m'
            str+= ("\n")
        return str

    #To remove a point from the set, call this function, the point will remain in space but the values are set to x.x
    def remove_point(self,row,col):
        if row < 0 or row >= self.size:
            raise IndexError
        if col < 0 or col >= self.size:
            raise IndexError
        point = self.grid[row][col]
        point.row = "x"
        point.col = "x"

    #If we attempt to create a path, but we've made mistake, we want to go back and fix our previous groups
    #This method allows us to set an x.x cord back to its original state
    def recover_cord(self,row,col):
        #print(self.__str__())
        if row < 0 or row >= self.size:
            raise IndexError
        if col < 0 or col >= self.size:
            raise IndexError
        point = self.grid[row][col]
        point.row = row
        point.col = col
        #print(self.__str__())

    #Recovers a list of coords, useful when a group generates other points that can't be connected
    def recover_group(self,cord_list):
        #print("recovering group")
        for cord in cord_list:
            self.recover_cord(cord[0],cord[1])
            p = self.grid[cord[0]][cord[1]]
            p.color = 37


    #Verifies if a point exists and isn't xed out
    def valid_point(self,row,col):
        #out of bounds check
        if row < 0 or row >= self.size:
            return False
        if col < 0 or col >= self.size:
            return False
        point = self.grid[row][col]
        #non removed point check
        if point.row != "x" and point.col != "x":
            return True
        return False

    #Get the count of neighbors a particular coordinate has
    def get_neighbors_values(self,row,col):
        if row < 0 or row >= self.size:
            raise IndexError
        if col < 0 or col >= self.size:
            raise IndexError
        up = self.valid_point(row-1, col)
        down = self.valid_point(row+1, col)
        left = self.valid_point(row, col-1)
        right = self.valid_point(row, col+1)
        return (up + down + left + right)

    #Return a list of valid/non xed out coordinates
    def get_neighbors_coords(self,row,col):
        if row < 0 or row >= self.size:
            raise IndexError
        if col < 0 or col >= self.size:
            raise IndexError
        up = self.valid_point(row-1, col)
        down = self.valid_point(row+1, col)
        left = self.valid_point(row, col-1)
        right = self.valid_point(row, col+1)
        coords = []
        if up:
            coords.append([row-1, col])
        if down:
            coords.append([row+1, col])
        if left:
            coords.append([row, col-1])
        if right:
            coords.append([row, col+1])
        return coords

    #After removing a set of points when creating a group, many points next to the group have lost their neighbors
    #This function recalculates the neighbors
    def check_all_neighbors(self):
        for row in range(self.size):
            for col in range(self.size):
                p = self.grid[row][col]
                neighbors = self.get_neighbors_values(row,col)
                p.neighbors = neighbors

    #It seems to be ideal to create paths starting with points with fewer options first, thus we start a path with the
    # point that has the fewest neighbors
    def find_index_start(self):
        row_best = 0
        col_best = 0
        min_neighbors = 999999
        for row in range(self.size):
            for col in range(self.size):
                if self.valid_point(row,col):
                    p = self.grid[row][col]
                    if p.neighbors < min_neighbors:
                        min_neighbors = p.neighbors
                        row_best = row
                        col_best = col
        return [row_best,col_best]

    #Given a coordinate and a color, we set the color of the point
    def set_color(self,row,col,color):
        if row < 0 or row >= self.size:
            raise IndexError
        if col < 0 or col >= self.size:
            raise IndexError
        point = self.grid[row][col]
        point.color = color

    #Given a list of lists of coordinate numbers, we assign those groups a particular color for visualization purposes
    #We chose colors that seem kinda distinct using https://talyian.github.io/ansicolors/
    def set_colors_from_groups(self,groups):
        colors = [31,32,33,34,35,36,39,90,95,92,93,94]
        for i in range(len(groups)):
            color = colors[i%len(colors)]
            for coord in groups[i]:
                self.set_color(coord[0],coord[1],color)

#Here is the obect that creates the groups
class Gerrymanderer:
    
    def __init__(self, startgrid):
        #We initalize an initial grid and a copy which we will manipulate to generate groups
        self.startgrid = startgrid
        self.workablegrid = copy.deepcopy(self.startgrid)
        self.groups = []


    def free_node_check(self,grid):
        def find_gap_size(workable_grid,count,row,col):
            #Once we are invalid, return the count
            if not workable_grid.valid_point(row,col):
                return count
            else:
                #print(str(row) + " " + str(col))
                workable_grid.remove_point(row,col)
                count = count + 1
                count = find_gap_size(workable_grid, count, row - 1, col)
                count = find_gap_size(workable_grid, count, row + 1, col)
                count = find_gap_size(workable_grid, count, row, col - 1)
                count = find_gap_size(workable_grid, count, row, col + 1)
                return count


        workable_grid = copy.deepcopy(grid)
        for row in range(self.startgrid.size):
            for col in range(self.startgrid.size):
                if not workable_grid.valid_point(row,col):
                    continue
                gap_size = find_gap_size(workable_grid,0,row,col)
                #print("GAPSIZE = " + str(gap_size))
                if gap_size % self.startgrid.size != 0:
                    return False
        return True






    #Create move creates one district grouping, this is a complex function which attempts to make progress forward but
    #may get stuck and thus move backwards...trying again with a different random choice. The main logic of this function
    #is getting a set of possible moves: UP, LEFT, DOWN, RIGHT (a subset of this based on valid moves)
    #from a starting coordinate and the randomly choosing a direction....checking if we get stuck
    def create_move(self):
        new_group = []
        workable_grid = copy.deepcopy(self.workablegrid)
        #set the starting point from the neighbor minimization function
        start = self.workablegrid.find_index_start()
        coord_move = start
        #make sure to pop this point off from our free coordinate grid
        workable_grid.remove_point(coord_move[0], coord_move[1])
        #add this point to our district group
        new_group.append(coord_move)
        num_steps_until_move_back_move = 4
        move_count = 1
        stuck_count = 0
        itercount = 0
        #we stop iterating when have a district with the desired size
        while move_count < self.startgrid.size:
            if itercount >= self.startgrid.size + 1: #infinite loop where we cannot find a valid group... so we give up
                return []
            #generate move options from previos coordinate
            move_options = workable_grid.get_neighbors_coords(coord_move[0],coord_move[1])

            if not move_options:
                #if there are no options we are at a dead end
                last_choice = new_group.pop()
                #We recover a previous coordinate we thought was part of the group but isn't since there aren't any options forward from it
                workable_grid.recover_cord(last_choice[0],last_choice[1])
                #If we are out of options and we just started our group...this is bad and we give up. There must have
                #been a bad group created earlier that messed this one up
                if not new_group:
                    return []
                #get the previous coordinate that may be the problem causing our dead end
                coord_move = new_group[-1]
                stuck_count+= 1
                move_count-=1
                #if we were stuck in this loop for a while we move back ANOTHER step...thus we could iteratively move back numerous steps in our path if need be
                if stuck_count >= num_steps_until_move_back_move:
                    last_choice = new_group.pop()
                    workable_grid.recover_cord(last_choice[0],last_choice[1])
                    if not new_group:
                        return []
                    coord_move = new_group[-1]
                    stuck_count = 0
                    move_count -= 1
                continue
            #We now assume that we have chosen a valid move that does not generate a dead end.. so pick a random direction from the valid set

            coord_move = random.choice(move_options)
            workable_grid.remove_point(coord_move[0],coord_move[1])
            new_group.append(coord_move)
            #print(new_group)
            move_count+= 1
            itercount += 1

        #We exited our while loop, meaning we generated a full path!
        for coords in new_group:
            #apply the change the main grid instead of the local one we have doing previously
            self.workablegrid.remove_point(coords[0],coords[1])
        return new_group

    def make_groups(self):
        self.startgrid = Grid(self.startgrid.size)
        self.workablegrid = copy.deepcopy(self.startgrid)
        # This attempts per branch variable is really important as it affects the amount of work done looking at a branch before giving up and trying a different branch
        # Increasing this could make sense for move complicated/larger grids but comes at the expense of major computation time
        attempts_per_branch = 4
        group_number_iters = [0] * self.startgrid.size
        groups = [[]] * self.startgrid.size
        group_number = 0
        start_time = time.time()
        #We want to generate the necessary number of groups/distrincts
        while group_number < self.startgrid.size:
            #If we did not generate a valid district (from the create move function above)
            while not groups[group_number]:
                #print(group_number_iters)
                #We try again for the most part, maybe we got unlucky with randomness
                groups[group_number] = self.create_move()
                #print(groups[group_number])
                self.workablegrid.set_colors_from_groups(groups)
                #print(self.workablegrid)



                invalid_move = not self.free_node_check(self.workablegrid)
                group_number_iters[group_number] += 1
                #If we try to generate a group and keep failing, there likely was a previous group messing us up
                #This means a previous group likely surrounded a point...making it impossible to put into a group
                if invalid_move and (group_number > 0):
                    #The solution is to look at the last group generated and redo that one, since it's breaking future groups
                    #print("HERE" + str(group_number))
                    #group_number_iters[group_number] = 0
                    #group_number-=1
                    self.workablegrid.recover_group(groups[group_number])
                    groups[group_number] = []
                    group_number -= 1
                elif (group_number_iters[group_number] > attempts_per_branch) and (group_number > 1):
                    #print("MOVING BACK 2")
                    #print("Group Number" + str(group_number))
                    group_number_iters[group_number] = 0
                    self.workablegrid.recover_group(groups[group_number])
                    groups[group_number] = []
                    group_number -= 1
                    group_number_iters[group_number] = 0
                    self.workablegrid.recover_group(groups[group_number])
                    groups[group_number] = []
                    group_number -= 1

            group_number+=1

            #We are taking too long and are stuck in some sort of loop moving up and back trying to find groups that don't block each other
            #If we are taking too long then try again
            current_time = time.time()
            time_limit = 2
            if current_time - start_time >= time_limit:
                print("Took too long, trying again")
                return False
        self.groups = groups
        return True

    #Keep trying if the time limit keeps getting hit
    def make_groups_time_limit(self):
        counter = 0
        while not self.make_groups():
            if counter > 10:
                default_groups = []
                for row in range(self.startgrid.size):
                    default_district = []
                    for col in range(self.startgrid.size):
                        default_district.append([row, col])               
                    default_groups.append(default_district)
                self.groups = default_groups
                return
            counter+=1

    def gerrymander(self, electorate, party):
        size = electorate.district_size()
        pairs = generate_district_pairings(size, 15)
        best_score = -1
        best_pair = None
        for pair in pairs:
            
            pair = transform_coordinates_to_indices(pair, size)
            
            result = electorate.get_wins(pair, party)
            if result > best_score:
                best_score = result
                best_pair = pair
        print(pair)
        return best_pair


def transform_coordinates_to_indices(groups, grid_size):
    """
    Transforms a list of coordinate pairs into a list of indices for each district group.

    Parameters:
    - groups: List of lists of coordinates (e.g., [[[0, 0], [0, 1], ...], ...])
    - grid_size: The size of the grid (e.g., 9 for a 9x9 grid)

    Returns:
    - A list of lists of indices (e.g., [[0, 1, 2, 3, 4, ...], ...])
    """
    transformed_groups = []
    for group in groups:
        # Convert each coordinate pair to its 1D index
        transformed_group = [r * grid_size + c for r, c in group]
        transformed_groups.append(transformed_group)
    
    return transformed_groups
        


#The function that generates the grid and the groups
def get_pairing_and_display(grid_size):
    grid = Grid(grid_size)
    groups = Gerrymanderer(grid)
    groups.make_groups_time_limit()
    grid.set_colors_from_groups(groups.groups)
    print(grid)
    return groups.groups

#Generates iters pairings of size grid_size
def generate_district_pairings(grid_size, iters):
    size = grid_size
    with ThreadPoolExecutor(max_workers=iters) as executor:
        args = []
        for i in range(iters):
            args.append(size)
        row_data = executor.map(get_pairing_and_display, args)
    district_pairs = list(row_data)
    return district_pairs

if __name__ == "__main__":
    gr = Grid(3)
    g = Gerrymanderer(gr)
    e = Electorate(3)
    party = True
    g.gerrymander(e, party)

