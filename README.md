# [Western Electric rules](https://www.wikiwand.com/en/Western_Electric_rules)
Python project to implement Western Electric Company rules (WECO) Version 0.2.1

## Table of Contents
- [Western Electric rules](#western-electric-rules)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
    - [There are 4 primary WE rules:](#there-are-4-primary-we-rules)
    - [There are 4 supplemental / trending WE rules:](#there-are-4-supplemental--trending-we-rules)
  - [Requirements](#requirements)
  - [Deployment / Usage](#deployment--usage)
  - [Future goals](#future-goals)
  - [Known issues](#known-issues)
  - [CodeStyle](#codestyle)
  - [Badges](#badges)
  - [Footnotes](#footnotes)

## About
1. Take input of data
2. Calculate points that fall out of each rule
3. Graph data
4. Show/indicate/flag points that violate rules

- [Defininitions of WECO rules](https://quinn-curtis.com//index.php/spcnamedrulesets/)
- [Interpreting WECO findings](https://www.spcforexcel.com/knowledge/control-chart-basics/control-chart-rules-interpretation)

### There are 4 primary WE rules:
1. The most recent point plots outside one of the 3-sigma control limits[^1]
2. Two of the three most recent points plot outside and on the same side as one of the 2-sigma control limits.[^2]
3. Four of the five most recent points plot outside and on the same side as one of the 1-sigma control limits.[^3]
4. Eight out of the last eight points plot on the same side of the center line, or target value.[^4]

### There are 4 supplemental / trending WE rules:
5. Six points in a row increasing or decreasing[^5]
6. Fifteen points in a row within one sigma[^6]
7. Fourteen points in a row alternating direction[^7]
8. Eight points in a row outside one sigma[^8]

## Requirements

  * Python 3.7 or greater

> This code makes use of the `f"..."` or [f-string syntax](https://www.python.org/dev/peps/pep-0498/). This syntax was introduced in Python 3.6.

For additional requirements and dependencies, please see the requirements.txt file.

## Deployment / Usage
This module simply introduces the WECO class object. Usage will require citation elsewhere or additional files within this project.

## Future goals
- [ ] Additional integrated testing (list support, checking graphs?)

## Known issues
1. N/A


## CodeStyle
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Flake8 Status](./reports/flake8/badge.svg)](./reports/flake8/index.html)
[![Coverage Status](./reports/coverage/badge.svg)](./reports/coverage/badge.svg)
[![pre-commit enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## Badges
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylecuberg/PyTemplate.svg)](https://github.com/kylecuberg/PyTemplate/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylecuberg/PyTemplate.svg)](https://github.com/kylecuberg/PyTemplate/pulls)
[![Python](https://img.shields.io/pypi/pyversions/cookiecutter-hypermodern-python-instance)](https://www.python.org/downloads/release/python-3100/)

## Footnotes
[^1]: If a point lies outside either of these limits, there is only a 0.3% chance that this was caused by the normal process.
[^2]: The probability that any point will fall outside the warning limit is only 5%. The chances that two out of three points in a row fall outside the warning limit is only about 1%.
[^3]: In normal processing, 68% of points fall within one sigma of the mean, and 32% fall outside it. The probability that 4 of 5 points fall outside of one sigma is only about 3%.
[^4]: Sometimes you see this as 9 out of 9, or 7 out of 7. There is an equal chance that any given point will fall above or below the mean. The chances that a point falls on the same side of the mean as the one before it is one in two. The odds that the next point will also fall on the same side of the mean is one in four. The probability of getting eight points on the same side of the mean is only around 1%. The Nelson Rules will change this to nine out of nine.
[^5]: The same logic is used here as for rule 4 above. Sometimes this rule is changed to seven points rising or falling.
[^6]: In normal operation, 68% of points will fall within one sigma of the mean. The probability that 15 points in a row will do so, is less than 1%.
[^7]: The chances that the second point is always higher than (or always lower than) the preceding point, for all seven pairs is only about 1%.
[^8]: Since 68% of points lie within one sigma of the mean, the probability that eight points in a row fall outside of the one-sigma line is less than 1%.

<!--[Format Guideline](https://docs.github.com/en/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)-->