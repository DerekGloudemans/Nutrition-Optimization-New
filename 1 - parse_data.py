# take data from raw csv files and 
# parse into a list (food ids) and numpy array (serving size, nutrition...)


import numpy as np
import csv
import _pickle as cPickle



# 1.Create list of all food ID numbers (NDB_No) and name (dicts)
food_list = []
file1 = open('Data/FOOD_DES.csv', encoding = 'utf-8')
csv_reader = csv.reader(file1,delimiter = ',')

for item in csv_reader:
    food_item = {}
    food_item["food_id"] = item[0]
    food_item["food_name"] = item[2]
    food_list.append(food_item)
    
print("All food items appended to food_list")
file1.close()



# 2. Go through nutrient list and for each food-nutrient combo, append to matching dict
food_nutrient_list = []

# each line of Nutrients.csv:
# ['NDB_No', 'Nutrient_Code', 'Nutrient_name', 'Derivation_Code', 'Output_value', 'Output_uom']
file2 =  open('Data/NUT_DATA.csv', encoding = 'utf-8')
csv_reader = csv.reader(file2, delimiter = ',')

for item in csv_reader:
    #represents one food and nutrient pair
    food_nutrient = {}
    # append food id, nutrient id, ammount
    food_nutrient["food_id"] = item[0]
    food_nutrient["nutrient_id"] = item[1]
    food_nutrient["value"] = item[2]
    food_nutrient_list.append(food_nutrient)

print("All food nutrient pairs appended to food_nutrient_list")
file2.close()    


# 3. Create list of all nutrients

# used to store unique nutrients
all_nutrients = []

file3 =  open('Data/NUTR_DEF.csv', encoding = 'utf-8')
csv_reader = csv.reader(file3, delimiter = ',')

for item in csv_reader:
    nutrient = {}
    nutrient["nutrient_id"] = item[0]
    nutrient["unit"] = item[1]
    nutrient["tag"] = item[2]
    nutrient["nutrient_name"] = item[3]
    all_nutrients.append(nutrient)
        
print("All unique nutrients identified")


# 4. Create numpy array for all nutrients, all foods

# First remove first row (labels) for each stored list
all_nutrients = all_nutrients[1:]
food_list = food_list[1:]
food_nutrient_list = food_nutrient_list[1:]

food_nutrient_mat = np.zeros([len(food_list),len(all_nutrients)])


# 5. Transfer info from dictionary to numpy list

# for each item in the food_nutrient list
count = 0
for item in food_nutrient_list:
    food_id = 0
    nutrient_id = 0
    #iterate through all food, nutrient combos and if match, transfer to array 
    for i in range(0,len(food_list)):
        if item["food_id"] == food_list[i]["food_id"]:
            food_id = i
            break
    for j in range(0,len(all_nutrients)):
        # if food and nutrient match the food and nutrient at j and i, respectively
        if item["nutrient_id"] == all_nutrients[j]["nutrient_id"]:
            nutrient_id = j   
            break
    food_nutrient_mat[food_id,nutrient_id] = item["value"]

    count = count + 1
    if count % 1000 == 0:
        print("On data point {}".format(count))
           


# 6. Create label lists for numpy array

# 7. Pickle these final data structure

# Commented for safety
#f = open("Nutrition_Data_Matrix.cpkl", 'wb')
#cPickle.dump((food_list,all_nutrients,food_nutrient_mat),f)
#f.close()
#print("All data pickled.")