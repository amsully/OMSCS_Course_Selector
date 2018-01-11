# OMSCS_Course_Selector

[CAUTION] A new developer has taken ownership of omscentral.com. API's may have been changed resulting in needed modifications of this code.

Not sure which class to take? Allow this script to do the thinking for you!

![alt text](https://github.com/amsully/OMSCS_Course_Selector/blob/master/omscs_selector.gif "Selector use case")

### Purpose

1. Select from a list of every OMSCS class.
2. Choose the metrics you want to rank by. 
3. Weight each metric based on what you value for your upcoming semester. 
4. The script pulls the data from https://omscentral.com/, normalizes the data and returns a ranking!

Results are saved in a local directory and can be viewed later. This script inverts difficulty and workload for you. The lower the difficulty and workload the higher the value is.


### Requirements:

python 3, requests library

All testing performed with python 3.6 on macOS.

### How to Use:

Install requests module if not already installed:

```
pip install requests
```

Run code
```
git clone https://github.com/amsully/OMSCS_Course_Selector.git

cd OMSCS_Course_Selector

python run.py
```

### Contribute

I whipped this up so if you notice an egregious errors add an issue or submit a pull request. Thanks!
