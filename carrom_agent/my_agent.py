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

#holes =[(22.21,22.21),(22.21,800-22.21),(800-22.21,22.21),(800-22.21,800-22.21)]
holes =[(44.1, 44.1), (755.9, 44.1), (755.9, 755.9), (44.1, 755.9)]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
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


first=True
#170:630
while 1:
        tm = s.recv(1024)
        try:
            S,r=parse_state_message(tm)
            print r
        except:
            print "Something went wrong",tm
   
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
            angle=math.atan2((to_hit[1]-loc[1]),(to_hit[0]-loc[0]))
            if angle < 0:
                angle = angle + 2*3.14
            angle=angle/3.14*180
            if angle>=315 and angle<=360:
                angle=angle-360

            a=a=str(float(x-170)/float(460))+','+str(angle)+ ','+str(0.8)
    #         if(first):
				# a=a=str(1)+','+str(math.atan2((S["Red_Location"][0][1]-145),(S["Red_Location"][0][0]-630))/3.14*180)+ ','+str(0.6)
				# first=False
                #a=str(angle)+ ',' + str(float(x-170)/float(460))+','+str(random.random()/1.25) # Remove in actual test
                #a=str(angle)+ ',' + str(float(x-170)/float(460))+','+str(0.5*dist2/800) # Remove in actual test
        else:
            a=None
        try:
            #print a + ":::" + str(to_hit) + "+++" + str(loc)
            s.send(a)
        except:
            print "Error in sending:",  a
	    print "Closing Connection"
	    break
s.close()
