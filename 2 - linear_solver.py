# optimize as a linear program with nutrient guidelines as constraints
from scipy.optimize import linprog
from scipy.optimize import minimize
import pickle
import csv
import numpy as np
import pandas as pd

def prep_data():
    # 1. load data from pickle files
    f = open("Data/Nutrition_Data_Matrix.pkl", 'rb')
    data_all = pickle.load(f)
    f.close()
    food_names = data_all[0] 
    nut_names = data_all[1]
    data = data_all[2]  
    
    
    # 2. Load exclusion lists 
    # Read constraint and nutrient inclusion values from excel
    df = pd.read_excel("Data/nut_constraints.xlsx")
    constraints = df.values
    
    nutrient_exclusion_list = constraints[2,:]
    constraints = constraints[0:2,:]
       
    #Read in food exclusion list from excel
    food_exclusion_list = []
    df2 = pd.read_excel("Data/food_exclusions.xlsx")
    food_exclusion_list = df2.values
    
    weights = food_exclusion_list[1,:]
    food_mins = food_exclusion_list[2,:]/100
    food_maxs = food_exclusion_list[3,:]/100
    food_exclusion_list = food_exclusion_list[0,:]
    
    
    # 3. Simplify data using exclusion lists
    food_idx = []
    for i in range(0,len(food_exclusion_list)):
        if food_exclusion_list[i] == 1:
            food_idx.append(i)
            
    nut_idx = []
    for i in range(0,len(nutrient_exclusion_list)):
        if nutrient_exclusion_list[i] == 1:
            nut_idx.append(i)
    
    # Selects only relevant data based on exclusion values
    data = data[food_idx,:]
    data = data[:,nut_idx]
    constraints = constraints[:,nut_idx]
    
    weights = weights[food_idx]
    food_mins = food_mins[food_idx]
    food_maxs = food_maxs[food_idx]
    
    #pairs mins and maxes into (min, max) bounds
    bounds = []
    for i in range(0,len(food_mins)):
        bounds.append((food_mins[i],food_maxs[i]))
    
    
    # Updates label lists to remove excluded food items
    new_food_names = []
    for item in food_idx:
        new_food_names.append(food_names[item])    
    food_names = new_food_names
    new_nut_names = []
    for item in nut_idx:
        new_nut_names.append(nut_names[item])    
    nut_names = new_nut_names
    
    return data, nut_names, food_names, constraints, weights, bounds

    
def display_result(data_in):
    result = data_in[0]
    food_names = data_in[3]
    nut_names = data_in[2]
    data = data_in[1]
    x = result.x
    mass = result.fun * 100
    
    included_foods = []
    for i in range(0,len(x)):
        if x[i] > 0.0001:
            included_foods.append((food_names[i]['food_name'], x[i]))
            
    print("Warning: highly optimal diet comin' up:\n")
    for item in included_foods:
        print("Eat {} grams of {}.".format(item[1]*float(100),item[0])) 
        
    
    data = np.transpose(data)
    x = x.reshape(-1,1)
    
    print("\nThis diet contains the following nutrients:\n")
    nuts = np.matmul(data,x)
    for i in range(0, len(nuts)):
        print("{} {} of {}".format(nuts[i,0],nut_names[i]['unit'], \
              nut_names[i]['nutrient_name']))


def lin_solver(data,nut_names, food_names, constraints, weights,bounds, weighting = -1, show = False):
    # Problem formulation notes:
    # each x-value corresponds to the amount (in 100 of grams) of one food
    # each constraint corresponds to a bound on a nutrient
    # Thus, for 2000 foods and 50 nutrients:
    # A should be 100 rows by 2000 columns
    # b should be 100 rows by 1 column
    # c should be 2000 columns by 1 row
    
    # Define upper bound constraints
    # idx will store indices of all defined max constraints
    idx = []
    A_max = np.transpose(data)
    b_max = constraints[1,:]
    for i in range(0,len(b_max)):
        # constraint is defined if not a nan
        if not(np.isnan(b_max[i])):
            idx.append(i)
    
    # Thus, A_max times x must be less than b_max
    A_max = A_max[idx,:]
    b_max = b_max[idx]
    
    # Define lower bound constraints
    idx = []
    A_min = np.transpose(data)
    b_min = constraints[0,:]
    for i in range(0,len(b_min)):
        # constraint is defined if not a nan
        if not(np.isnan(b_min[i])):
            idx.append(i)
    
    # Thus, A_min times x must be less greater than b_min 
    A_min = A_min[idx,:]
    b_min = b_min[idx]
    # So -A_min times x must be less than -b_min 
    A_min = -A_min
    b_min = -b_min
    
    # Finished LP formulation
    A = np.concatenate((A_min,A_max), axis = 0)
    b = np.concatenate((b_min,b_max), axis = 0)
    
    # define objective (min weight, none, min all but selected food weights)
    if weighting == -1:
        c = np.ravel(np.ones([np.size(A,1), 1]))
    elif weighting == 0:
        c = np.ravel(np.zeros([np.size(A,1), 1]))
    else:
        c = np.ravel(np.ones([np.size(A,1), 1]))
        for i in range (0,len(weights)):
            if weights[i] != 0:
                c[i] = 0
    
    
    #Run linear program solver
    result = linprog(c, A_ub=A, b_ub=b, bounds = bounds,method = 'interior-point')
    
    
    if show:
    #6. Display results
        display_result((result,data, nut_names,food_names))    
    return result, (A,b,c)

def iter_removal_solver(data,nut_names, food_names, constraints, weights, weighting = 1, step_size = 1, show = False):
    #let's try solving, removing all variables below some threshold weight, solve again, etc.
    solveable = True
    all_results = []
    count = 1
    
    
    while solveable:
         if show:
             print("On iteration {}.".format(count))
         
         result,(A,b,c) = lin_solver(data,nut_names,food_names,constraints,weighting,show = False)
         
         if result.status != 0:#unsolveable
             solveable = False
         else:
             count = count + 1
             all_results.append((result,data,nut_names,food_names))
             
             #remove 10-lowest-weight values from A, c, food_names
             x1 = result.x
             x1 = x1.reshape(-1,1)
             sort = np.argsort(x1[:,0])
             remaining = sort[step_size:]
             
             A = A[:,remaining]
             c = c[remaining]
             data = data[remaining,:]
             
             food_names2 = []
             for i in range(0,len(remaining)):
                 food_names2.append(food_names[remaining[i]])
             food_names = food_names2
             

             
             
    if show:
        display_result((all_results[-1]))
    return result2

################################ BEGIN BODY CODE ##############################




#load data
data, nut_names, food_names, constraints, weights, bounds = prep_data()

#run linear program solver
result, junk = lin_solver(data,nut_names, food_names, constraints,weights,bounds, weighting = 1, show = True)
x = result.x
weight = result.fun * 100    
    
# run iterative removal solver
#result2 = iter_removal_solver(data,nut_names, food_names, constraints,weights, weighting = -1, step_size = 1, show = True)   
    
    
