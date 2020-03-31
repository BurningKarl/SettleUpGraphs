# SettleUpGraphs
Automatically create beautiful graphs of your expenses in SettleUp

## Usage

1. Clone this repository: `git clone https://github.com/BurningKarl/SettleUpGraphs.git && cd SettleUpGraphs`
1. Set up your python environment: `virtualenv env && source env/bin/activate && pip install -r requirements.txt`
1. Use email export from SettleUp and put the `transactions.csv` file into the current folder
1. Run `python main.py`
1. Open `SettleUpGraphs.html` with your webbrowser and view the generated graphs

*Note:* This tool makes use of the SettleUp categories, which is a paid feature at the moment. 
If you don't have this feature you can fill in your categories in the corresponding column in the CSV file and get the same result.

## FAQ

* **How do I restrict the graphs to a subset of all expenses?**  
  Just remove the unecessary expenses from the CSV file but be sure to leave the header (first line) in otherwise the first expense will be ignored.
  
* **How do I exclude some of the names?**  
  This feature is not implemented yet, it isn't possible.
  
* **How do I generate other graphs / a subset of these graphs?**  
  The current graphs are hardcoded inside the `main.py` so you can change them there.
  
## Tools

* This script relies heavily on the visualization library [Bokeh](bokeh.org).
