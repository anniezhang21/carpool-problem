# project-fa19
CS 170 Fall 2019 Project

The main solver is within solver.py and it is run in the way specified in the spec, i.e.
```python3 solver.py --all ./inputs ./outputs```
For the solver to run correctly, it must be in the same directory as tsp_helper.py.

Our solver utilizes an external Traveling Salesman Problem (tsp) solver from Google's ortools library.
The modified version of the tsp solver is located in tsp_helper.py.

Additional dependencies:
ortools


