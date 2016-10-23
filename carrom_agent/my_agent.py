from Utils import *
import time
import socket
import math
import sys
from thread import *
import ast
import numpy as np
import argparse
import random
from one_step import simulate

parser = argparse.ArgumentParser()

parser.add_argument('-np', '--num-players', dest="num_players", type=int,
                    default=1,
                    help='1 Player or 2 Player')
parser.add_argument('-p', '--port', dest="PORT", type=int,
                        default=12121,
                        help='Port')

parser.add_argument('-rs', '--random-seed', dest="rng", type=int,
                    default=0,
                    help='Random Seed')
parser.add_argument('-c', '--color', dest="color", type=str,
                    default="Black",
                    help='Legal color to pocket')
args=parser.parse_args()




host = '127.0.0.1'
port = args.PORT
random.seed(args.rng)
#holes =[(22.21,22.21),(22.21,800-22.21),(800-22.21,22.21),(800-22.21,800-22.21)]
holes =[(44.1, 44.1), (755.9, 44.1), (755.9, 755.9), (44.1, 755.9)]

def parse_state_message(msg):
    s = msg.split(";REWARD")
    s[0] = s[0].replace("Vec2d", "")
    reward = float(s[1])
    state = ast.literal_eval(s[0])
    return state, reward

def get_coin_max_sep(coin_list) :
    maxi_index = 0
    maxi_dist = 100000
    dist = 0
    for i in range(0,len(coin_list)) :
        dist = get_dist(coin_list,i)
        if dist < maxi_dist :
            maxi_dist = dist
            maxi_index = i
    return maxi_index

def get_dist(coin_list, index) :
    distance = 0;
    for j in range(0,len(coin_list)):
        distance = distance + dist(coin_list[j],coin_list[index])
    return distance

def find_nearest_hole(coin) :
    maxi_index = 0
    maxi_dist = 0
    distance = 0
    holes1=[]
    for hole in holes:
    	m=(coin[1]-hole[1])/(coin[0]-hole[0])
    	c=coin[1]-m*coin[0]
    	x=(145-c)/m
    	# del=math.asin(POCKET_RADIUS,dist(hole,coin))/3.14*180
    	if(170<x and x<630):
    		holes1.append(hole)
    if(len(holes1)>0):
	    for j in range(0,len(holes1)):
	        distance = dist(holes1[j],coin)
	        if distance > maxi_dist :
	            maxi_dist = distance
	            maxi_index = j
	    return holes1[maxi_index]
    for j in range(0,len(holes)):
        distance = dist(holes[j],coin)
        if distance > maxi_dist :
            maxi_dist = distance
            maxi_index = j
    return holes[maxi_index]

def vectorize_state(state):
	ans=np.zeros((38))
	i=0
	for x in state["White_Locations"]:
		ans[i]=x[0]
		ans[i+1]=x[1]
		i+=2
	i=18	
	for x in state["Black_Locations"]:
		ans[i]=x[0]
		ans[i+1]=x[1]
		i+=2
	i=36
	for x in state["Red_Location"]:
		ans[i]=x[0]
		ans[i+1]=x[1]
	return ans
def get_most_suitable_x(list_of_x,coin_list,to_hit, angle_to_hole) :
    max_max_travelable_dist = 0
    random.shuffle(list_of_x)
    index = 0
    
    y = 145
    x=to_hit[0] + (y-to_hit[1])*math.tan(angle_to_hole)
    if(x<630 and x>170):
    	return x,dist(to_hit,(x,y))

    for i in range (0,len(list_of_x)) :
        unobstructed_distance = (to_hit[0] - list_of_x[i])*(to_hit[0] - list_of_x[i]) + (to_hit[1] - 145)*(to_hit[1] - 145)
        #angle = math.atan2((to_hit[1]-145),(to_hit[0]-list_of_x[i]))
        minx = min(list_of_x[i], to_hit[0])
        maxx = max(list_of_x[i], to_hit[0])
        miny = min(145, to_hit[1])
        maxy = max(145, to_hit[1])
        for j in range(0,len(coin_list)):
            if coin_list[j][0] >= minx and coin_list[j][0] <= maxx and coin_list[j][1] >= miny and coin_list[j][1] <= maxy :
                distance = dist(coin_list[j],(list_of_x[i],145))
                if distance < unobstructed_distance :
                    unobstructed_distance = distance
        if unobstructed_distance == dist(to_hit,(list_of_x[i],145)):
            return list_of_x[i], unobstructed_distance

        if unobstructed_distance > max_max_travelable_dist : 
            max_max_travelable_dist = unobstructed_distance
            index = i
    return list_of_x[index], max_max_travelable_dist

def play(S):
    if  len(S["White_Locations"])!=0 or len(S["Black_Locations"])!=0 or len(S["Red_Location"])!=0:
    	to_hit_list=S["Black_Locations"]+S["Red_Location"] + S["White_Locations"]
    if len(to_hit_list) == 2 and len(S["Red_Location"])!=0 :
        to_hit = S["Red_Location"][0]
    else :
        try:
            to_hit = to_hit_list[get_coin_max_sep(to_hit_list)]
        except:
            to_hit = (400,400)
    hole = find_nearest_hole(to_hit)

    angle_to_hole = math.atan2((to_hit[1]-hole[1]),(to_hit[0]-hole[0]))
    list_of_x = range(170,640,10)
    x,dist2 = get_most_suitable_x(list_of_x,to_hit_list,to_hit, angle_to_hole)
    loc = (x,145)
    if(dist(loc,to_hit)<40):
    	if(x<590):
    		x+=40
    	else:
    		x-=40
    loc = (x,145)
    angle=math.atan2((to_hit[1]-loc[1]),(to_hit[0]-loc[0]))
    if angle < 0:
        angle = angle + 2*3.14
    angle=angle/3.14*180
    if angle>=315 and angle<=360:
        angle=angle-360
    force=0.8*(1+0.001*sqrt(dist2))
    if(angle<0 or angle>180):
    	force = 0.1
    angle1=math.atan2((hole[1]-loc[1]),(hole[0]-loc[0]))/3.14*180
    if(abs(angle-angle1)<10):
    	force = 0.1    
    return str(float(x-170)/float(460))+','+str(angle)+ ','+str(force)
def myplay(S):
	if  len(S["White_Locations"])!=0 or len(S["Black_Locations"])!=0 or len(S["Red_Location"])!=0:
		to_hit_list=S["Black_Locations"]+S["Red_Location"] + S["White_Locations"]
	if len(to_hit_list) == 2 and len(S["Red_Location"])!=0 :
		to_hit = S["Red_Location"][0]
	if(len(to_hit_list)>4):
		return None
	targets=[]
	for coin in to_hit_list:
		for hole in [(755.9, 755.9), (44.1, 755.9)]:
			if(dist(coin,hole)<45):
				continue
			m=(coin[1]-hole[1])/(coin[0]-hole[0])
			c=coin[1]-m*coin[0]
			x=(145.0-c)/m
			# del=math.asin(POCKET_RADIUS,dist(hole,coin))/3.14*180
			ang=math.atan2((coin[1]-145),(coin[0]-x))/3.14*180
			if ang < 0:
				ang = ang + 360
			if ang>=315 and ang<=360:
				ang=ang-360
			if(170<x and x<630 and ang<=225 and ang>=-45 ):
				#find # obstructions
				obtr=0
				for co in to_hit_list:
					if(dist((x,145),co)<35):
						obtr=10
					if(abs(co[1]-m*co[0]-c)/sqrt(1+m*m) <25):
						obtr+=1
				if(obtr<=1):
					targets.append((coin,hole,x,ang,obtr))
	min_dist = 10000
	idx=0			
	for i in range(len(targets)):
		if(min_dist>dist(targets[i][0],targets[i][1])):
			min_dist=dist(targets[i][0],targets[i][1])
			idx=i
	if(targets!=[]):
		print targets[idx]
		d=dist((targets[idx][2],145),targets[idx][0])+1.05*dist(targets[idx][0],targets[idx][1])
		return str(float(targets[idx][2]-170)/float(460))+','+str(targets[idx][3])+ ','+str(0.002*sqrt(d)*sqrt(targets[idx][4]))    
	return None
a_old=None
if __name__ == "__main__":
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	first=True
	#170:630
	while 1:
	    tm = s.recv(1024)
	    try:
	        S,r=parse_state_message(tm)
	    except:
	        print "Something went wrong",tm
			
	    a=play(S)
	    if(a==None):
	    	a=play(S)
	    	print "Default"
	    if(first):
			a="1.0, 131.7829, 0.5"
			first=False
				# first=False
	            #a=str(angle)+ ',' + str(float(x-170)/float(460))+','+str(random.random()/1.25) # Remove in actual test
	            #a=str(angle)+ ',' + str(float(x-170)/float(460))+','+str(0.5*dist2/800) # Remove in actual test
	    try:
	        #print a + ":::" + str(to_hit) + "+++" + str(loc)
	        if(a_old==a):
	        	a="2,-60,0.8"
	        a_old=a
	        s.send(a)
	    except:
	        print "Error in sending:",  a
	    	print "Closing Connection"
	    	break
	s.close()
