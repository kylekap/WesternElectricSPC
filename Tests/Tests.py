import csv
#import Project.core as core
from context import Project

def read_practice_data(filename="Tests/TestData.csv", numrows=1000):
    results = []
    with open(filename) as inputfile:
        for row in csv.reader(inputfile):
            if row[0] in ["Male", "Female"]:
                results.append(float(row[2]))
                if len(results) > numrows:
                    break
    return results

def main():
    li = read_practice_data(numrows=750)
    test = Project.core.WECO(li, "Male Height")#, wecorules=["7"], annotatelist=["7"])
    test.ViolationsCSV()
    test.graph()


if __name__ == "__main__":
    """[summary]"""
    main()
