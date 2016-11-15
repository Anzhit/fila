from scipy.optimize import minimize
from one_step import simulate
from Utils import *
import numpy as np

def f(c):
	result=0
	for i in range(1000):
		result+= -1*simulate(INITIAL_STATE,[0.5,c[0],c[1]],i)[1]
		print result*1.0/(i+1)
	return result/25.0
f([90,1])
# minimize(f,[123.81651347599552, 0.50472986095589867],method='nelder-mead',options={'disp': True})