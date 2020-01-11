# project-fa19
CS 170 Fall 2019 Project

Annie Zhang, Ada Hu, Lily Sai

#### Problem Statement
You are given an undirected graph G = (L,E) where each vertex in L is a location. You are also given a starting location s, and a list H of unique locations that correspond to homes. The weight of each edge (u,v) is the length of the road between locations u and v, and each home in H denotes a location that is inhabited by a TA (teaching assistant). Traveling along a road takes energy, and the amount of energy expended is proportional to the length of the road. For every unit of distance traveled, the driver of the car expends 32 units of energy, and a walking TA expends 1 unit of energy. The car must start and end at s, and every TA must return to their home in H.
You must return a list of vertices vi that is the tour taken by the car (cycle with repetitions allowed), as well as a list of drop-off locations at which the TAs get off. You may only drop students off at vertices visited by the car, and multiple TAs can be dropped off at the same location.
We’d like you to produce a route and sequence of drop-offs that minimizes total energy expenditure, which is the sum of the driver’s energy spent driving and the total energy that all of the TAs spend walking. TAs do not expend any energy while sitting in the car. Assume that TAs will take the shortest path home from whichever location they are dropped off at.

#### Algorithm Overview
See ```Final_report.pdf```.

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
```147_200.in```,
```345_50.in```.

For both solvers to run correctly, they must be in the same directory as ```tsp_helper.py```.

For inputs ```184_50.in```, ```184_100.in```, and ```184_200.in```, the output files were manually written.

#### Dependencies:
```networkx``` (https://networkx.github.io/documentation/stable)
```ortools``` (https://developers.google.com/optimization/install)

Our solver utilizes an external Traveling Salesman Problem (tsp) solver from Google's ```ortools``` library.
The modified version of the tsp solver is located in ```tsp_helper.py```.


