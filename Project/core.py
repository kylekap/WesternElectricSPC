import matplotlib.pyplot as plt
import csv


class WECO:
    def __init__(self, li, variable_name="Variable"):
        self.data = [x for x in li if type(x) in [int, float]]  # clean non-numeric
        self.variable_name = variable_name

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
            self.zabs, sigmalimit=1, qtypoints=8, qtylimit=8, outside=False
        )
        self.weco7 = self.rule7(self.data)
        self.weco8 = self.PrimaryRules(self.zabs, sigmalimit=0, qtypoints=8, qtylimit=8)

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

        res = [False for x in range(len(data))]
        for i in range(len(data) - (qtypoints - 1)):
            li = data[i : i + (qtypoints)]

            if outside:
                countup = len([x for x in li if x > sigmalimit])
                countdown = len([x for x in li if x < -sigmalimit])
            else:
                countup = len([x for x in li if x < sigmalimit])
                countdown = len([x for x in li if x > -sigmalimit])

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

    def rule7(self, data, qtypoints=14):
        """res = [False for x in range(len(data))]

        for i in range(len(data) - (qtypoints - 1)):
            li = data[i : i + (qtypoints)]
            modli = []
            for j in range(len(li)-1):
                modli.append(li[j+1]-li[j])

        """
        return

    def WECOOutliers(self, boolindex, datalist, rounding=1):
        li = []
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

        # Rules 1-4
        plt.plot(
            xs,
            self.data,
            markevery=self.weco1,
            marker="D",
            markeredgewidth=3,
            ls="",
            mfc="none",
            label="Beyond Limits",
            markersize=marker * 4,
        )
        plt.plot(
            xs,
            self.data,
            markevery=self.weco2,
            marker="o",
            markeredgewidth=3,
            ls="",
            mfc="none",
            label="Zone A",
            markersize=marker * 3.75,
        )
        plt.plot(
            xs,
            self.data,
            markevery=self.weco3,
            marker="v",
            markeredgewidth=3,
            ls="",
            mfc="none",
            label="Zone B",
            markersize=marker * 3.5,
        )
        plt.plot(
            xs,
            self.data,
            markevery=self.weco4,
            marker="^",
            markeredgewidth=3,
            ls="",
            mfc="none",
            label="Zone C",
            markersize=marker * 3.25,
        )

        # Rules 5-8
        plt.plot(
            xs,
            self.data,
            markevery=self.weco4,
            marker="s",
            markeredgewidth=2,
            ls="",
            mfc="none",
            label="Trending",
            markersize=marker * 2,
        )
        plt.plot(
            xs,
            self.data,
            markevery=self.weco4,
            marker="s",
            markeredgewidth=2,
            ls="",
            mfc="none",
            label="Stratification",
            markersize=marker * 2,
        )
        plt.plot(
            xs,
            self.data,
            markevery=self.weco4,
            marker="s",
            markeredgewidth=2,
            ls="",
            mfc="none",
            label="Over-Control",
            markersize=marker * 2,
        )
        plt.plot(
            xs,
            self.data,
            markevery=self.weco4,
            marker="s",
            markeredgewidth=2,
            ls="",
            mfc="none",
            label="Mixture",
            markersize=marker * 2,
        )

        for rule in [self.weco1]:
            for val in self.WECOOutliers(rule, self.data, rounding=1):
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
    test = WECO(li, "Male Height")
    test.graph()


if __name__ == "__main__":
    """[summary]"""
    main()
