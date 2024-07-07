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
    # Initialize a new array with the same shape as depth_array, filled with 1000
    new_depth_array = np.full_like(depth_array, 1000.0)
    depth_change_points = []

   
   

    # Iterate through each row of the depth array
    for row in range(depth_array.shape[0] - 1):
        flag=0
        for col in range(depth_array.shape[1]):
            if(depth_array[row, col] !=0):
            # Check for the condition where depth changes from <10 to >10
                if depth_array[row + 1, col] < 2000 and depth_array[row, col] > 2000:
                    depth_change_points.append((row, col, depth_array[row + 1, col]))
                    new_depth_array[row + 1, col] = depth_array[row + 1, col]
                    flag=1
            
                if(flag==1):
                    continue

    ####
  ####
    for col in range (new_depth_array.shape[1]):
        if(depth_array[1,col]<2000 and depth_array[1,col]>0):
            new_depth_array[1,col]=depth_array[1,col]

                    ####
                 

    return new_depth_array, depth_change_points

def visualize_depth_data(file_path):
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    im = None

    front_horizontal_distance_pub = rospy.Publisher('/front_horizontal_distance', Float32, queue_size=10)
    front_height_pub = rospy.Publisher('/front_height', Float32, queue_size=10)
    # far_dict_pub = rospy.Publisher('/far_dict', String, queue_size=10)

    # highest_height_value = -np.inf
    # highest_height_value_pixel = None
    # far_d_of_highest = None
    # rate = rospy.Rate(10)


    while not rospy.is_shutdown():
        try:
            # Check if the file exists
            if os.path.exists(file_path):
                # Load the depth array from the file
                depth_array = np.load(file_path)
                
                if depth_array.size != 0:
                    # Process the depth array to detect depth changes
                    new_depth_array, depth_change_points = process_depth_data(depth_array)

                    far_dict = {}

                    # start_row, end_row = 0, 400
                    # start_col, end_col = 0, 600

                    # new_depth_array = new_depth_array[start_row:end_row, start_col:end_col]


                    # Initialize far_h to a large value
                    far_h = new_depth_array.shape[0]
                    temp = 0

                    # before=np.copy(new_depth_array)

                    # for r in range(before.shape[0]):
                    #     for c in range(before.shape[0]):
                    #         if before[r, c] < 900:
                    #             far_d=before[r,c]
                    #             far_d=far_d*math.cos(global_pitch)
                    #             far_h=200-r
                    #             far_h= horizontal_distance= math.tan((3.14*0.15*(far_h)/180)-global_pitch)*far_d
                    #             # if(height_value>=0):
                    #             #     height_value= (1-0.001*math.pow(far_d,3))*height_value

                    #             # else:
                    #             #     height_value= (1+0.001*math.pow(far_d,3))*height_value

                    #             # if height_value > highest_height_value:
                    #             #     highest_height_value = height_value
                    #             #     highest_height_value_pixel = (r, c)
                    #             #     far_d_of_highest = far_d

                    #             if far_d not in far_dict and far_d<10:
                    #                 far_dict[far_d] = []
                    #             far_dict[far_d].append(far_h)

                    # for key in far_dict:
                    #     far_dict[key] = max(far_dict[key])

                    # far_dict_str = str(far_dict)
                    # far_dict_pub.publish(far_dict_str)

                    # print(f"Dictionary of far_d and max far_h: {far_dict}")
                    # far_dict.clear()



                    # Loop through the depth array to find the minimum row index (far_h)
                    for r in range(new_depth_array.shape[0] - 1):
                       
                        for c in range(new_depth_array.shape[1]):
                            if new_depth_array[r, c] < 900:
                                #new filter for warping
                                # new_depth_array[r, c] = (1-0.001*math.pow(new_depth_array[r, c],3))*new_depth_array[r, c]
                                if r < far_h:
                                    far_h = r
                                    temp = c
                                  
                                elif r == far_h and c < temp:
                                    temp = c
                                 

                          
                    print(global_pitch)

                    # for r in range(new_depth_array.shape[0] - 1):
                       
                    #     for c in range(new_depth_array.shape[1]):
                    #         print(new_depth_array[r,c], end=" ")

                        

                    if far_h < new_depth_array.shape[0]:
                        far_d = new_depth_array[far_h, temp]
                        far_h = 200*(1-math.sin(global_pitch))- far_h
                    else:
                        far_d = 1000


                    far_d=far_d*math.cos(global_pitch)

                    height_value= horizontal_distance= math.tan((3.14*0.14*(far_h)/180))*far_d

                    print("prev_far_h:", height_value)

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
                    # print("transformed d",far_d_of_highest)
                    # print("transformed h",highest_height_value)
                    # print("Transformed Height Value:", transformed_height_value)

                    if im is None:
                        im = ax.imshow(new_depth_array, cmap='viridis')
                        plt.colorbar(im, ax=ax, label='Depth (meters)')
                        plt.title('Depth Map Visualization')
                        plt.xlabel('Width (pixels)')
                        plt.ylabel('Height (pixels)')
                    else:
                        im.set_data(new_depth_array)
                        ax.draw_artist(ax.patch)
                        ax.draw_artist(im)
                        fig.canvas.flush_events()

                    plt.pause(0.1)
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
