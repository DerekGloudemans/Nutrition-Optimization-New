# Nutrition-Optimization-New
Implements a linear program solver to create an optimal diet based on a large database of foods and nutritional content. 

Nutritional data was obtained by downloading the database files from the USDA's Food Composition Database. This dataset contains nutritional content information for over 9000 foods and over 100 nutrients. 

1 - data_parse.py is used to convert these .csv files into a more human-readable form, where each row of the CSV represents a food and each column represents a nutrient.

2 - linear_solver.py is used to formulate the task of selecting a diet with optimal nutritional content as a linear program. Nutritional minimums and maximums are input as constraints to the program, and the objective function seeks to minimize the overall weight of selected foods. As of now, the mechanism for interacting with the solver is a bit clunky, and I am still thinking of a more elegant way to input constraints, etc. 

In the food_exclusions.xlsx file, the first column indicates whether the food should be included at all in the optimization. The second column indicates whether the food's weight should count towards the objective function. The solver will attempt to use only foods that do not count towards the overall weight first, so one can easily specify a set of base ingredients that the solver will always attempt to use first. The third and fourth columns specify the minimum and maximum allowable weight of that food in the solution.

In the nut_constraints.xlsx, the first and second columns correspond to the daily min and max values for each nutrient.

All nutritional content values can be viewed in data_chart.xlsx

To generate a diet, modify the nut_constraints and food_exclusions files, then run linear_solver.py. A diet will be output indicating the weight of each food included in the diet as well as the overall nutritional content of the diet.

This repository isn't really in a finished state yet, but if you're interested in using it, let me know and I'll be happy to answer any questions to get it up and running for you!
