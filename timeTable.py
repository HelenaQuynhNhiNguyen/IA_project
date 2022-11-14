#IMPORTING THE LIBRARIES
from random import randint,sample
from ortools.sat.python import cp_model
import os

#CREATE THE INPUT FILE
#NOTE : 
#WE DIDNT HAVE A BASE INPUT FILE TO TEST SO WE CREATED A GENERATOR FUNCTION THAT RANDOMLY GENERATES COURSES FOR A NUMBER OF INSTRUCTORS
#HOWEVER, THE RANDOMNESS MEANS THAT SOME CONFIGURATIONS DO NOT HAVE A SOLUTION

def input_generator():
    #FOR THIS GENERATOR WE CHOSE THIS CONFIGURATION : 3,5,2,3,3 FOR A 5 DAY WEEK
    num_instructors = 3
    num_courses = 5
    num_lectures = 2
    max_courses_in_day = 2
    max_courses_per_instructor = 3
    week = 5

    input = open(os.path.dirname(__file__) + "\input_timeTable.txt", "w")
    input.write("%i,%i,%i,%i,%i\n" %(num_instructors,num_courses,num_lectures,max_courses_in_day,max_courses_per_instructor)) #first line with constants
    for i in range(num_instructors):
        A=sample(range(0,num_courses),randint(1,max_courses_per_instructor)) #random courses generated for each professor
        input.write(str(A)+"\n")
    return week


#READ THE INPUT FILE AND FORMAT IT

week = input_generator() #ignore/comment if the input file is provided
data = open(os.path.dirname(__file__)+"\input_timetable.txt","r") #Change path to the input file if provided
file = data.read()


#READING THE CONSTANTS OF THE FILE
constants = [int(j) for j in file.split("\n")[0].split(",")]

#Number of instructors: nI
num_instructors = constants[0]

#Number of courses: nC
num_courses = constants[1]

#Number of lectures for a course in a week: mL
num_lectures = constants[2]

#Max courses taught in a day: mD
max_courses_in_day = constants[3]

#Max courses per instructor: mC
max_courses_per_instructor = constants[4]


#DEFINING THE RANGES
all_courses = range(num_courses)
all_instructors = range(num_instructors)
week = range(num_instructors,num_instructors+week)


#READING THE COURSES TO BE TAUGHT BY TEACHER
data = file.split("\n")[1:-1]
for i in range(len(data)):
    #Creating a list of list with every sublist being the courses taught by i-th instructor
    data[i]=[int(j) for j in data[i].replace("[","").replace("]","").split(",")] #Reading and formating at the same time


#CONVERTING THE DATA MATRIX TO A BOOLEAN MATRIX :
#COLUMNS : COURSES
#ROWS : INSTRUCTORS
#ELEMENTS : IF THE COURSE IS TAUGHT BY THE INSTRUCTOR

data = [[course in data[instructor] for course in all_courses] for instructor in all_instructors]


#CREATING THE MODEL
model = cp_model.CpModel()


#ADD VARIABLES
timetable = {} #2-D DICTIONARY
for course in all_courses: #each line is for a course
    for instructor in all_instructors: #First nI columns are for the instructors
        timetable[(course,instructor)] = model.NewBoolVar('Course %i' %course)
    for day in week: #Last 5 columns are for the days of the week
        timetable[(course,day)] = model.NewIntVar(0,num_lectures,'Course %i' %course)


#ADD CONSTRAINTS
#CONSTRAINT N°0 : All instructors teach specific courses
for instructor in all_instructors:
    for course in all_courses:
        if not data[instructor][course]: #Presence in the boolean matrix
            model.Add(timetable[(course,instructor)] == 0) #No instructor will teach a course they can't teach

#CONSTRAINT N°1 : "Each course is taught by exactly one instructor"
for course in all_courses:
    #model.AddExactlyOne(timetable[(course,instructor)] for instructor in all_instructors) #For some reason, this breaks the code
    model.Add(sum(timetable[(course,instructor)] for instructor in all_instructors) == 1) #Equivalent to the one above

#CONSTRAINT N°2 : "Each course has exactly mL (e.g., 2) lectures per week."
for course in all_courses:
    model.Add(sum(timetable[(course,day)] for day in week) == num_lectures)  

#CONSTRAINT N°3 : "During one day of the week, there may not be more than mD lectures."
for day in week:
    model.Add(sum(timetable[(course,day)] for course in all_courses) <= max_courses_in_day)

#CONSTRAINT N°4 : "An instructor teaches a maximum of mC courses."
for instructor in all_instructors:
    model.Add(sum(timetable[(course,instructor)] for course in all_courses) <= max_courses_per_instructor)


#CREATE SOLVER 
solver = cp_model.CpSolver()


#PRINTING OUT THE SOLUTION
#CREATE THE OUTPUT FILE
output = open(os.path.dirname(__file__)+"\output_timeTable.txt","w")


#CREATE THE SOLUTION PRINTER
def SolutionPrinter(solver):
    
    for i in all_courses: #All courses
        line = "Course " + str(i) + "," #Line to be printed

        for instructor in all_instructors:
            if solver.BooleanValue(timetable[(i,instructor)]):
                value_instructor = instructor+1 #Instructor teaches this course, +1 to avoid instructor starting at 0
        line = line + " Instructor " + str(value_instructor) + ","

        for day in week:
            line = line + " day %i : %i lecture(s), " %(day-num_instructors+1, solver.Value(timetable[(i,day)])) #Shows how many lectures there are for each day
        line = line + "\n"
        print(line)
        output.write(line)


#CREATE ALL THE FEASIBLE SOLUTION PRINTER

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    
    """Print intermediate solutions."""
    def __init__(self, variables,l):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables__ = variables
        self.__solution_count = 0
        self.__nb_solutions_limit = l

    def on_solution_callback(self): #Standard function used to print all solution found
        self.__solution_count += 1
        if(self.__solution_count<=self.__nb_solutions_limit):
            print(f"\nSolution {self.__solution_count}\n") #Solution counter printed
            SolutionPrinter(self)
            print("-------------------")
            output.write("-------------------") #Space to separate the solution

    def solution_count(self):
        return self.__solution_count

num_solution = 5 #Number of solutions generated, called "l" in the problem statement
printer = VarArraySolutionPrinter(timetable,num_solution)
solver.parameters.enumerate_all_solutions = True #Will show all the solution
status = solver.Solve(model, printer)
output.close()

