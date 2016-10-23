import tensorflow as tf
import numpy as np
import tflearn
from one_step import simulate
from Utils import *
from replay_buffer import ReplayBuffer
from my_agent import play

# =========================
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
class Environment(object):

    def __init__(self):
        self.S=INITIAL_STATE
        print "New Episode"
    def reset(self):
        self.S=INITIAL_STATE
        return vectorize_state(self.S)
    def step(self,action):
        a=play(self.S)
        a=map(float,a.split(","))
        self.S,r=simulate(self.S,[a[0],a[1],action*0.01])
        print "Reward",r
        if(len(self.S["White_Locations"])==0 and len(self.S["Black_Locations"])==0 and len(self.S["Red_Location"])==0 ):
            return vectorize_state(self.S),r,True
        return vectorize_state(self.S),r,False
    def seed(self,a):
        return

env = Environment()

inputs1 = tf.placeholder(shape=[1,38],dtype=tf.float32)
W = tf.Variable(tf.random_uniform([38,50],0,0.01))
W1 = tf.Variable(tf.random_uniform([50,100],0,0.01))
Qout = tf.matmul(tf.nn.relu(tf.matmul(inputs1,W)),W1)
predict = tf.argmax(Qout,1)

#Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
nextQ = tf.placeholder(shape=[1,100],dtype=tf.float32)
loss = tf.reduce_sum(tf.square(nextQ - Qout))
trainer = tf.train.AdamOptimizer(learning_rate=0.001)
updateModel = trainer.minimize(loss)
init = tf.initialize_all_variables()

# Set learning parameters
y = .99
e = 0.1
num_episodes = 30
#create lists to contain total rewards and steps per episode
jList = []
rList = []
with tf.Session() as sess:
    sess.run(init)
    for i in range(num_episodes):
        #Reset environment and get first new observation
        s = env.reset()
        rAll = 0
        d = False
        j = 0
        #The Q-Network
        while j < 99:
            j+=1
            #Choose an action by greedily (with e chance of random action) from the Q-network
            print np.count_nonzero(s)
            a,allQ = sess.run([predict,Qout],feed_dict={inputs1:[s]})
            if np.random.rand(1) < e:
                a[0] = random.randint(0,99)
            #Get new state and reward from environment
            s1,r,d = env.step(a[0])
            #Obtain the Q' values by feeding the new state through our network
            Q1 = sess.run(Qout,feed_dict={inputs1:[s1]})
            #Obtain maxQ' and set our target value for chosen action.
            maxQ1 = np.max(Q1)
            targetQ = allQ
            targetQ[0,a[0]] = r + y*maxQ1
            #Train our network using target and predicted Q values
            _,W1 = sess.run([updateModel,W],feed_dict={inputs1:[s],nextQ:targetQ})
            rAll += r
            s = s1
            if d == True:
                #Reduce chance of random action as we train the model.
                e = 1./((i/50) + 10)
                break
        jList.append(j)
        print jList