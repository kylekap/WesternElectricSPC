import matplotlib.pyplot as plt
import csv

# List of elements to boolean
# https://stackoverflow.com/questions/30446510/list-of-elements-to-boolean-array


class WECO:
    def __init__(self, li, variable_name="Variable"):
        self.data = [x for x in li if type(x) in [int, float]]  # clean non-numeric
        self.variable_name = variable_name
        # pre-calculate useful values
        self.av = self.WecoAv()
        self.std = self.WecoStd()
        self.z = self.WecoZ()
        self.zabs = [abs(x) for x in self.z]

        # calculate rules
        self.weco1 = self.Rule1()
        self.weco2 = self.Rule2()
        self.weco3 = self.Rule3()
        self.weco4 = self.Rule4()

    def WecoAv(self):
        return round((sum(self.data) / len(self.data)), 5)

    def WecoStd(self):
        variance = sum([((x - self.av) ** 2) for x in self.data]) / len(self.data)
        return round((variance**0.5), 5)

    def WecoZ(self):
        li = []
        for val in self.data:
            li.append(round((val - self.av) / self.std, 5))
        return li

    def Rule1(self, limit=3):
        return [True if x > limit else False for x in self.zabs]

    def Rule2(self, limit=2):
        res = [False for x in range(len(self.zabs))]
        for i in range(len(self.zabs) - 2):
            li = self.zabs[i : i + 3]
            count = len([x for x in li if x > limit])
            if count >= 2:
                res[i + 2] = True
        return res

    def Rule3(self):
        return []

    def Rule4(self):
        return []

    def graph(self):
        xs = [x for x in range(len(self.data))]
        plt.plot(
            xs,
            self.data,
            color="black",
            linewidth=1,
            marker="o",
            markerfacecolor="blue",
            markersize=4,
        )
        self.plotAxlines()
        self.plotFormat()
        plt.show()

    def plotAxlines(self):
        colors = ["black", "lightgreen", "gold", "darkred"]
        for level, color in enumerate(colors):
            upper = self.av + self.std * level
            lower = self.av - self.std * level
            plt.axhline(y=upper, linewidth=1, color=color)
            plt.axhline(y=lower, linewidth=1, color=color, label=f"{level} sigma")
        return

    def plotFormat(self):
        plt.title("Western Electric SPC chart")
        plt.xlabel("Instance #")
        plt.ylabel(self.variable_name + " Value")
        plt.legend(loc="best")


def read_practice_data(filename="Tests/TestData.csv"):
    results = []
    with open(filename) as inputfile:
        for row in csv.reader(inputfile):
            if row[0] == "Male":
                results.append(float(row[2]))
            if len(results) > 1000:
                break
    return results


def main():
    li = read_practice_data()
    test = WECO(li, "Male Height")
    test.graph()
    # print(test.z)
    # print(1,test.weco1)
    # print(2,test.weco2)
    # print(3,test.weco3)
    # print(4,test.weco4)


if __name__ == "__main__":
    """[summary]"""
    main()
