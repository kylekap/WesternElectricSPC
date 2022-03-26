import csv
from operator import is_
import numpy as np
import matplotlib.pyplot as plt


# 6,7,8 do not work in the graph?


class WECO:
    def __init__(
        self,
        li,
        variable_name="Variable",
        wecorules=["1", "2", "3", "4", "5", "6", "7", "8"],
        annotatelist=[],
    ):
        """_summary_

        Args:
            li (_type_): _description_
            variable_name (str, optional): _description_. Defaults to "Variable".
            wecorules (list, optional): _description_. Defaults to ["1", "2", "3", "4", "5", "6", "7", "8"].
            annotatelist (list, optional): _description_. Defaults to [].
        """
        self.data = [x for x in li if type(x) in [int, float]]  # clean non-numeric
        self.variable_name = str(variable_name)
        self.applyrules = [
            x for x in wecorules if x in ["1", "2", "3", "4", "5", "6", "7", "8"]
        ]
        self.annotatelist = [
            x for x in annotatelist if x in ["1", "2", "3", "4", "5", "6", "7", "8"]
        ]

        # pre-calculate useful values
        self.av = self.WecoAv()
        self.std = self.WecoStd()
        self.z = self.WecoZ()
        self.zabs = [abs(x) for x in self.z]

        # calculate Primary rules
        """ 1 - The most recent point plots outside one of the 3-sigma control limits
            2 - Two of the three most recent points plot outside and on the same side as one of the 2-sigma control limits.
            3 - Four of the five most recent points plot outside and on the same side as one of the 1-sigma control limits.
            4 - Eight out of the last eight points plot on the same side of the center line, or target value.
        """
        self.weco1 = self.PrimaryRules(self.z, sigmalimit=3, qtypoints=1, qtylimit=1)
        self.weco2 = self.PrimaryRules(self.z, sigmalimit=2, qtypoints=3, qtylimit=2)
        self.weco3 = self.PrimaryRules(self.z, sigmalimit=1, qtypoints=5, qtylimit=4)
        self.weco4 = self.PrimaryRules(self.z, sigmalimit=0, qtypoints=8, qtylimit=8)

        # calculate Secondary rules
        """ 5. Six points in a row increasing or decreasing
            6. Fifteen points in a row within one sigma [similar to primary, but use abs because "within 1"]
            7. Fourteen points in a row alternating direction
            8. Eight points in a row outside one sigma [similar to primary, but use abs because "outside 1"]
        """
        self.weco5 = self.rule5(self.z, 6)
        self.weco6 = self.PrimaryRules(
            self.zabs, sigmalimit=1, qtypoints=15, qtylimit=15, outside=False
        )
        self.weco7 = self.rule7(self.data)
        self.weco8 = self.PrimaryRules(self.zabs, sigmalimit=1, qtypoints=8, qtylimit=8)

        self.rule_dict = {
            "1": self.weco1,
            "2": self.weco2,
            "3": self.weco3,
            "4": self.weco4,
            "5": self.weco5,
            "6": self.weco6,
            "7": self.weco7,
            "8": self.weco8,
        }

    def WecoAv(self):
        """Calculate mean of given self.data set.

        Returns:
            float: Mean value
        """
        return round((sum(self.data) / len(self.data)), 5)

    def WecoStd(self):
        """Calculate stddev of given self.data set.

        Returns:
            float: StdDev value
        """
        variance = sum([((x - self.av) ** 2) for x in self.data]) / len(self.data)
        return round((variance**0.5), 5)

    def WecoZ(self):
        """Calculate Z scores of given self.data set based on std & av

        Returns:
            list: Z scores of items
        """
        li = []
        for val in self.data:
            li.append(round((val - self.av) / self.std, 5))
        return li

    def PrimaryRules(self, data, sigmalimit=2, qtypoints=2, qtylimit=3, outside=True):
        """Most rules are variations of - "some qtypoints of the last qtylimit points are [< or >] than sigmalimit sigmas in the same direction".

        Functions combined to meet condition sets.

        Args:
            sigmalimit (int, optional): number of sigma (std deviations) to use as limit. Defaults to 3.
            qtypoints (int, optional): quantity of points to check bad side of sigmalimit. Defaults to 1.
            qtylimit (int, optional): quantity of points to fail test if fall bad side of sigmalimit. Defaults to 1.
            outside (bool, optional): check if values are outside (True) or inside (False) sigma limit.

        Returns:
            list : boolean list, failures represented by True
        """
        countdown = 0
        countup = 0

        res = [False for x in range(len(data))]
        for i in range(len(data) - (qtypoints - 1)):
            li = data[i : i + (qtypoints)]

            if outside:
                countup = len([x for x in li if x > sigmalimit])
                countdown = len([x for x in li if x < -sigmalimit])
            else:
                countup = len([x for x in li if (x < sigmalimit and x > -sigmalimit)])

            if countup >= qtylimit or countdown >= qtylimit:
                res[i + (qtypoints - 1)] = True
        return res

    def rule5(self, data, qtypoints=6):
        """

        Args:
            data (list): _description_
            qtypoints (int, optional): quantity of points to check if increasing/decreasing. Defaults to 6.

        Returns:
            _type_: _description_
        """
        res = [False for x in range(len(data))]
        for i in range(len(data) - (qtypoints - 1)):
            li = data[i : i + (qtypoints)]
            chk = all(i < j for i, j in zip(li, li[1:]))
            if chk:
                res[i + (qtypoints - 1)] = True
        return res

    def is_alternating_signs(self, a):
        return np.all(np.abs(np.diff(np.sign(a))) == 2)

    def rule7(self, data, qtypoints=14):
        res = [False for x in range(len(data))]
        modli = []
        for i in range(1, len(data)):
            if data[i] > data[i-1]:
                modli.append(1)
            else:
                modli.append(-1)

        for i in range(len(modli) - (qtypoints - 1)):
            li = modli[i : i + (qtypoints)]
            if(self.is_alternating_signs(li)):
                res[i+(qtypoints-1)] = True
        return res

    def WECOOutliers(self, boolindex, datalist, rounding=1):
        li = []
        if boolindex is not None and len(boolindex) > 0:
            a = [i for i, x in enumerate(boolindex) if x]
            for ea in a:
                tup = (ea, round(datalist[ea], rounding))
                li.append(tup)
        return li

    def graph(self):
        xs = [x for x in range(len(self.data))]
        marker = 4
        plt.style.use("fivethirtyeight")
        plt.plot(
            xs,
            self.data,
            marker="o",
            ls="",
            markerfacecolor="blue",
            markeredgecolor="blue",
            markersize=marker,
        )

        formatting = {
            "1": {"label": "Beyond Limits", "marker": "D", "markersizeadj": 4},
            "2": {"label": "Zone A", "marker": "o", "markersizeadj": 3.75},
            "3": {"label": "Zone B", "marker": "v", "markersizeadj": 3.5},
            "4": {"label": "Zone C", "marker": "^", "markersizeadj": 3.25},
            "5": {"label": "Trending", "marker": "s", "markersizeadj": 2},
            "6": {"label": "Stratification", "marker": "s", "markersizeadj": 2},
            "7": {"label": "Over-Control", "marker": "s", "markersizeadj": 2},
            "8": {"label": "Mixture", "marker": "s", "markersizeadj": 2},
        }

        for rule in self.applyrules:
            plt.plot(
                xs,
                self.data,
                markevery=self.rule_dict.get(rule),
                markeredgewidth=3,
                ls="",
                mfc="none",
                marker=formatting.get(rule, {}).get("marker", "o"),
                label=formatting.get(rule, {}).get("label", rule),
                markersize=marker * formatting.get(rule, {}).get("markersizeadj", 2),
            )

        if len(self.annotatelist) > 0:
            for rule in self.annotatelist:
                for val in self.WECOOutliers(
                    self.rule_dict.get(rule), self.data, rounding=1
                ):
                    plt.annotate(val, xy=val, fontsize=10)

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

    def ViolationsCSV(self, filename=r"Results/Outliers.CSV"):
        li = []
        for k, v in self.rule_dict.items():
            a = self.WECOOutliers(v, self.data, rounding=1)
            for val in a:
                temp = list(val)
                temp.append(k)
                li.append(temp)

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Item #", "Value", "Rule# Violated"])
            writer.writerows(li)


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
    #li = [1,2,1,3,2,4,3,5,4,5,3,6,4,7,6,7,6,7,6,7,6,7,6,7,6,7,6,7]
    test = WECO(li, "Male Height")#, wecorules=["7"], annotatelist=["7"])
    test.ViolationsCSV()
    test.graph()


if __name__ == "__main__":
    """[summary]"""
    main()
