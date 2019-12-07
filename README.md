# project-fa19
CS 170 Fall 2019 Project

Annie Zhang, Ada Hu, Lily Sai

#### Instructions to Reproduce Output
The main solver is within ```solver.py``` and it is run in the way specified in the spec, i.e.
```python3 solver.py --all ./inputs ./outputs```
However, for the following inputs, the output was obtained with ```solver0.py```, a simplified version of 
```solver.py```. It is run in the same way, i.e.```python3 solver0.py --all ./inputs ./outputs```

Special inputs:
```61_200.in```,
```105_200.in```,
```120_50.in```,
```147_50.in```,
```147_100.in```,
```137_200.in```,
```345_50.in```.

For both solvers to run correctly, they must be in the same directory as ```tsp_helper.py```.

For inputs ```184_50.in```, ```184_50.in```, and ```184_50.in```, the output files were manually written.

#### Dependencies:
All dependencies from the starter code.

```ortools``` (https://developers.google.com/optimization/install)

Our solver utilizes an external Traveling Salesman Problem (tsp) solver from Google's ```ortools``` library.
The modified version of the tsp solver is located in ```tsp_helper.py```.


