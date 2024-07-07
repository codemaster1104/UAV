import rospy
import math
import time
import matplotlib.pyplot as plt
import numpy as np
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32


class FCU_connection:

    def __init__(self):
        rospy.init_node('mavros_fcu')
        self.vel_pub = rospy.Publisher("/mavros/setpoint_velocity/cmd_vel_unstamped", Twist, queue_size=100)
        self.horizontal_distance_pub = rospy.Publisher('/horizontal_distance', Float32, queue_size=10)
        self.min_depth_value_pub = rospy.Publisher('/min_depth_value', Float32, queue_size=10)
        self.front_horizontal_distance_pub = rospy.Publisher('/front_horizontal_distance', Float32, queue_size=10)
        self.front_height_pub = rospy.Publisher('/front_height', Float32, queue_size=10)
        self.rate = rospy.Rate(20)

        self.horizontal_distance = Float32()
        self.min_depth_value = Float32()

        #initialse front altitude variables
        self.farr=0
        self.farh=0
        self.fard=10
        

         # forwad velocity
        self.f_vel=4
        ####################################################

        # PID controller parameters
        if(self.farh<0):
            self.Kp = 0.3/(self.fard+1)*math.exp(self.f_vel)
        else:
            self.Kp = 0.3/(self.fard+1)*math.exp(self.f_vel)

        self.Ki = 0.05
        self.Kd = 0.05
        
        # Target altitude
        self.target_altitude = 3.0
        self.prev_alt=0

        # Initialize bottom distance altitude
        self.bottom_altitude = 0.0
        self.bottomr=0
        self.bottom_angle=0
        
        # Variables for PID controller
        self.prev_error = 0.0
        self.integral = 0.0
        
        # arrays
        self.rangess_d=[]
        self.rangess_f=[]
        self.rangess=[]

        self.times = []
        self.farh_values = []
        self.error_values = []


        self.far_d_pub = rospy.Publisher("/far_d", Float32, queue_size=10)
        self.far_h_pub = rospy.Publisher("/far_h", Float32, queue_size=10)
        self.f_v_pub = rospy.Publisher("/f_v", Float32, queue_size=10)

        self.horizontal_distance_sub = rospy.Subscriber('/horizontal_distance', Float32, self.horizontal_distance_callback)
        self.min_depth_value_sub = rospy.Subscriber('/min_depth_value', Float32, self.min_depth_value_callback)
        self.front_horizontal_distance_sub = rospy.Subscriber('/front_horizontal_distance', Float32, self.front_horizontal_distance_callback)
        self.front_height_sub = rospy.Subscriber('/front_height', Float32, self.front_height_callback)

    def horizontal_distance_callback(self, data):
        self.horizontal_distance = data
        # self.print_values()

    def min_depth_value_callback(self, data):
        self.min_depth_value = data
        # self.print_values()

    def front_horizontal_distance_callback(self, data):
        self.front_horizontal_distance = data
        # self.print_values()

    def front_height_callback(self, data):
        self.front_height = data
        # self.print_values()

    def print_values(self):
        print("Horizontal Distance: ", self.horizontal_distance.data)
        print("Min Depth Value: ", self.min_depth_value.data)
        print("Front Horizontal Distance: ", self.front_horizontal_distance.data)
        print("Front Height: ", self.front_height.data)


    def pid_control(self):
        # Error calculation
        error = self.target_altitude 
    
        # Proportional term
        P = self.Kp * error
        # Integral term
        self.integral =(self.integral + error) * self.rate.sleep_dur.to_sec()
        I = self.Ki * self.integral
        # Derivative term
        derivative = (error - self.prev_error) / self.rate.sleep_dur.to_sec()
        D = self.Kd * derivative
        # PID output
        output = P + I + D
        if(output<-1):
            output=-1
        if (self.farh==0):
            output=0

        
        
        # Update previous error for next iteration
        self.prev_error = error
        
        # Apply the output to velocity
        vel_msg = Twist()
        vel_msg.linear.x = 0.0
        vel_msg.linear.y = self.f_vel
        vel_msg.linear.z = output
        vel_msg.angular.x = 0.0
        vel_msg.angular.y = 0.0
        vel_msg.angular.z = 0.0
        
        print("output: ",output)

        # Publish the velocity
        self.vel_pub.publish(vel_msg)

    def calculator(self):

        if math.isnan(self.front_height.data) or math.isnan(self.min_depth_value.data) or \
           math.isnan(self.front_horizontal_distance.data) or math.isnan(self.horizontal_distance.data):
            rospy.logwarn("One or more input values are NaN, setting defaults.")
            self.farh = 0.0
            self.fard = 100.0

        # if self.front_height.data>=0 :
        #     self.front_height.data=(1-0.001*math.pow(self.front_height.data,3))*self.front_horizontal_distance.data
        
        # if self.front_height.data<0 :
        #     self.front_height.data=(1+0.001*math.pow(self.front_height.data,3))*self.front_horizontal_distance.data

        
        if(((abs(self.front_height.data+3)/abs(self.front_horizontal_distance.data))*13>1) and self.front_height.data<100 and self.front_horizontal_distance.data<100):
            self.fard=self.front_horizontal_distance.data
            self.farh=self.front_height.data
            # self.fard=self.horizontal_distance.data
            # self.farh=self.min_depth_value.data


        else:
            self.fard=self.horizontal_distance.data
            self.farh=self.min_depth_value.data
            # self.fard=self.front_horizontal_distance.data
            # self.farh=self.front_height.data

        if(self.fard>20):
            self.fard=100
            self.farh=0

        if(self.fard<0):
            self.fard=100
            self.farh=0

        

        return self.farh, self.fard

    def maintain_altitude(self):
        time.sleep(1)

        start_time = time.time()
        while not rospy.is_shutdown():
            self.farh,self.fard=self.calculator()
            # self.target_altitude=((self.farh+3)/(self.fard+1))*math.exp(self.f_vel)
            self.target_altitude=self.farh+3

            print("fard: ",self.fard)
            print("farh: ",self.farh)
            print("tar alt: ",self.target_altitude)
            print(" ")

            self.pid_control()

            self.far_d_pub.publish(Float32(self.fard))
            self.far_h_pub.publish(Float32(self.farh))
            self.f_v_pub.publish(Float32(self.f_vel))

            current_time = time.time() - start_time
            self.times.append(current_time)
            self.farh_values.append(self.farh)
            self.error_values.append(self.target_altitude )

            self.rate.sleep()

        
    
if __name__ == '__main__':
    fcu = FCU_connection()
    try:
        fcu.maintain_altitude()
    except KeyboardInterrupt:
        print("Shutting down")



