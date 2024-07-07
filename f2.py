import numpy as np
import matplotlib.pyplot as plt
import time
import os
import math
import rospy
from std_msgs.msg import Float32, String
import tf
from sensor_msgs.msg import Imu

# Global variables to store roll, pitch, and yaw
global_roll = 0.0
global_pitch = 0.0
global_yaw = 0.0

def imu_callback(data):
    global global_roll, global_pitch, global_yaw

    # Extract quaternion from the message
    quaternion = (
        data.orientation.x,
        data.orientation.y,
        data.orientation.z,
        data.orientation.w
    )

    # Convert quaternion to Euler angles
    euler = tf.transformations.euler_from_quaternion(quaternion)

    # Update global roll, pitch, and yaw
    global_roll, global_pitch, global_yaw = euler

def imu_listener():
    # Initialize the ROS node
    
    rospy.Subscriber('/mavros/imu/data', Imu, imu_callback)

    # Keep the node running
    

def process_depth_data(depth_array):
   
    print("depth_array:", depth_array.shape[1])

    h_val=200
    d_val=1000
  
    # Iterate through each row of the depth array from top to bottom
    for row in range(depth_array.shape[0]):
        for col in range(depth_array.shape[1]):
            # Check for the condition where depth is less than 20
            if depth_array[row, col]!= 0 and depth_array[row, col] < 20:
                h_val = row
                d_val = depth_array[row, col]
                ####################################
                h_val=h_val
                d_val=d_val
                ####################################
                return h_val, d_val

    return h_val, d_val

  

def visualize_depth_data(file_path):
   
    front_horizontal_distance_pub = rospy.Publisher('/front_horizontal_distance', Float32, queue_size=10)
    front_height_pub = rospy.Publisher('/front_height', Float32, queue_size=10)
   

    while not rospy.is_shutdown():
        try:
            # Check if the file exists
            if os.path.exists(file_path):
                # Load the depth array from the file
                depth_array = np.load(file_path)
                
                if depth_array.size != 0:
                    # Process the depth array to detect depth changes
                    h, d = process_depth_data(depth_array)
                    far_d=d

                   

                    # start_row, end_row = 0, 400
                    # start_col, end_col = 0, 600

                    # new_depth_array = new_depth_array[start_row:end_row, start_col:end_col]


                    # Initialize far_h to a large value
                    far_h = h
                    print("far_h:", far_h)
                    

                    far_h = 200*(1-math.sin(global_pitch))- far_h
                    


                          
                    print(global_pitch)


                    far_d=far_d*math.cos(global_pitch)

                    height_value= horizontal_distance= math.tan((3.14*0.15*(far_h)/180))*far_d

                    print("height:", height_value)

                    #############################################
                    # if(height_value>=0):
                    #     height_value= (1-0.001*math.pow(far_d,3))*height_value

                    # else:
                    #     height_value= (1+0.001*math.pow(far_d,3))*height_value
                    #################################################


                    front_horizontal_distance_pub.publish(far_d)
                    front_height_pub.publish(height_value)

                    # print("final_far_h:", height_value)
                    print("far_d:", far_d)
                   
                else:
                    print("Empty depth array. Waiting for data...")
                    time.sleep(0.5)
            else:
                print(f"File '{file_path}' does not exist yet. Waiting...")
                time.sleep(0.5)
        except Exception as e:
            print("Error:", e)
            time.sleep(0.5)

if __name__ == '__main__':
    # Path to the file where depth data is saved
    imu_listener()
    rospy.init_node('depth_visualizer', anonymous=True)
    depth_file_path = "/tmp/front_depth_data.npy"
    
    visualize_depth_data(depth_file_path)
