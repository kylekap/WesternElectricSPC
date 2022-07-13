import csv as csv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class WECO:
    def __init__(self, data, variable_name="Variable", **kwargs):
        """_summary_

        Args:
            data (_type_): _description_
            variable_name (str, optional): _description_. Defaults to "Variable".

        KWArgs:
            cl (list of ints): list of control limit sigma values to plot. Defaults to [0, 1, 2, 3]
            USL (float): upper spec limit, as numeric value. Defaults to no plot.
            LSL (float): lower spec limit, as numeric value. Defaults to no plot.
            xaxis (string): xaxis name (must be dataframe column if using dataframe inputs). Defaults to "".
            wecorules (list): list of weco rules to plot. Defaults to [1, 2, 3, 4, 5, 6, 7, 8]
            annotations (list): list of weco violations to annotate. Defaults to []
        """
        self.variable_name = str(variable_name)
        self.data = self.weco_input_format(data)  # clean non-numeric
        self.weco_xaxis_format(kwargs.get("xaxis", ""))  # select X axis and labels
        self.applyrules = [
            x
            for x in kwargs.get("wecorules", ["1", "2", "3", "4", "5", "6", "7", "8"])
            if x in ["1", "2", "3", "4", "5", "6", "7", "8"]
        ]
        self.annotatelist = [x for x in kwargs.get("annotations", []) if x in ["1", "2", "3", "4", "5", "6", "7", "8"]]

        # pre-calculate useful values
        self.av = self.WecoAv()
        self.std = self.WecoStd()
        self.z = self.WecoZ()
        self.zabs = [abs(x) for x in self.z]

        self.cl = [x for x in kwargs.get("cl", range(0, 3, 1)) if type(x) in [int, float]]

        # Optional spec limit graphing
        if "USL" in kwargs:
            self.USL = kwargs.get("USL", "")
            self.plot_cl(self.USL, color="red", label="USL")
        if "LSL" in kwargs:
            self.LSL = kwargs.get("LSL", "")
            self.plot_cl(self.LSL, color="red", label="LSL")

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
        self.weco6 = self.PrimaryRules(self.zabs, sigmalimit=1, qtypoints=15, qtylimit=15, outside=False)
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
        variance = sum(((x - self.av) ** 2) for x in self.data) / len(self.data)
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

    def weco_input_format(self, data):
        """_summary_

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """
        if isinstance(data, list):
            return [x for x in data if type(x) in [int, float]]  # clean non-numeric

        if isinstance(data, type(pd.DataFrame())) and self.variable_name in data.columns:
            return pd.to_numeric(data[self.variable_name], errors="coerce")

        else:
            return False

    def weco_xaxis_format(self, x):
        """_summary_

        Args:
            x (_type_): _description_
        """
        if isinstance(self.data, type(pd.DataFrame())) and x in self.data.columns:
            self.xaxis_values = self.data[x]
            self.xaxis_title = x
        else:
            self.xaxis_values = [x for x in range(len(self.data))]
            self.xaxis_name = x

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

    def alternating_signs(self, a):
        """_summary_

        Args:
            a (_type_): _description_

        Returns:
            _type_: _description_
        """
        return np.all(np.abs(np.diff(np.sign(a))) == 2)

    def rule7(self, data, qtypoints=14):
        """_summary_

        Args:
            data (_type_): _description_
            qtypoints (int, optional): _description_. Defaults to 14.

        Returns:
            _type_: _description_
        """
        res = [False for x in range(len(data))]
        modli = []
        for i in range(1, len(data)):
            if data[i] > data[i - 1]:
                modli.append(1)
            else:
                modli.append(-1)

        for i in range(len(modli) - (qtypoints - 1)):
            li = modli[i : i + (qtypoints)]
            if self.alternating_signs(li):
                res[i + (qtypoints - 1)] = True
        return res

    def WECOOutliers(self, boolindex, datalist, rounding=1):
        """_summary_

        Args:
            boolindex (_type_): _description_
            datalist (_type_): _description_
            rounding (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        li = []
        if boolindex is not None and len(boolindex) > 0:
            a = [i for i, x in enumerate(boolindex) if x]
            for ea in a:
                tup = (ea, round(datalist[ea], rounding))
                li.append(tup)
        return li

    def graph(self):
        """_summary_"""

        xs = self.xaxis_values
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
                for val in self.WECOOutliers(self.rule_dict.get(rule), self.data, rounding=1):
                    plt.annotate(val, xy=val, fontsize=10)

        self.plot_cl()
        self.plotFormat()
        plt.show()

    def plot_cl(self, **kwargs):
        """Plots control limits"""
        colors = kwargs.get("colors", ["#008fd5", "#fc4f30", "#e5ae38", "#6d904f", "#8b8b8b", "#810f7c"])

        for level in self.cl:
            upper = self.av + self.std * level
            lower = self.av - self.std * level
            plt.axhline(y=upper, linewidth=1, color=colors[level])
            plt.axhline(y=lower, linewidth=1, color=colors[level], label=f"{level} sigma")
        return

    def plot_sl(self, sl, label, color):
        plt.axhline(y=sl, linewidth=1, color=color, label=label)

    def plotFormat(self):
        """_summary_"""
        plt.title("Western Electric SPC chart")
        plt.xlabel(self.xaxis_name)
        plt.ylabel(self.variable_name + " Value")
        plt.legend(loc="best")

    def ViolationsCSV(self, filename=r"Results/Outliers.CSV"):
        """_summary_

        Args:
            filename (regexp, optional): _description_. Defaults to r"Results/Outliers.CSV".
        """
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
        return li


def main():
    return None


if __name__ == "__main__":
    """[summary]"""
    main()
