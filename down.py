import numpy as np
import matplotlib.pyplot as plt
import time
import os
import math
import rospy
from std_msgs.msg import Float32,String
import tf
from sensor_msgs.msg import Imu


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



def visualize_depth_data(file_path):
    # plt.ion()  # Turn on interactive mode
    # # fig_before, ax_before = plt.subplots()
    # fig_after, ax_after = plt.subplots()
    # fig, ax = plt.subplots()
    # # im_before = None
    # im = None

    rospy.init_node('depth_visualizer', anonymous=True)
    horizontal_distance_pub = rospy.Publisher('/horizontal_distance', Float32, queue_size=10)
    min_depth_value_pub = rospy.Publisher('/min_depth_value', Float32, queue_size=10)
    down_dict_pub = rospy.Publisher('/down_dict', String, queue_size=10)

    while not rospy.is_shutdown():
        try:
            # Check if the file exists
            if os.path.exists(file_path):
                # Load the depth array from the file
                depth_array = np.load(file_path)
                # depth_value = depth_array[200, 590]
                # print(f"Depth value at (600, 200): {depth_value:.2f} meters")
                # centre_depth = depth_array[200, 300]
                # print(f"Depth value at (300, 200): {centre_depth:.2f} meters")

                start_row, end_row = 0, 400
                start_col, end_col = 200, 600

                down_dict={}

                # Extract the depth data for the specified range of pixels
                depth_array = depth_array[start_row:end_row, start_col:end_col]
                # before=np.copy(depth_array)
                # for r in range(depth_array.shape[0]):
                #     for c in range(depth_array.shape[1]):
                #         horizontal_distance= math.tan(3.14*0.15*(c-100)/180+global_pitch)*depth_array[r,c]
                #         depth_array[r,c]=-depth_array[r,c]
                #         depth_array[r,c]=depth_array[r,c]*math.cos(global_pitch)
                #         # depth_array[r,c]=depth_array[r, c]*(1+0.001*math.pow(horizontal_distance,3))


                #         if horizontal_distance not in down_dict and horizontal_distance<10:
                #             down_dict[horizontal_distance] = []
                #         down_dict[horizontal_distance].append(depth_array[r,c])

                # for key in down_dict:
                #     down_dict[key] = max(down_dict[key])

                # down_dict_str = str(down_dict)
                # down_dict_pub.publish(down_dict_str)

                # print(f"Dictionary of far_d and max far_h: {down_dict}")
                # down_dict.clear()


                min_depth_index = np.argmin(depth_array)

                # Convert the flattened index to row and column indices
                min_depth_row, min_depth_col = np.unravel_index(min_depth_index, depth_array.shape)

                # Get the depth value at the pixel with the least depth
                min_depth_value = depth_array[min_depth_row, min_depth_col]

                min_depth_value = min_depth_value*math.cos(global_pitch)

                horizontal_distance= math.tan(3.14*0.15*(min_depth_col-100)/180)*min_depth_value

                min_depth_value=-min_depth_value
                if(min_depth_value<-100 or min_depth_value>100):
                    min_depth_value=0

                if(horizontal_distance<-100):
                    horizontal_distance=1000


                horizontal_distance_pub.publish(horizontal_distance)
                min_depth_value_pub.publish(min_depth_value)

                # print("Prev_Minimum depth value:", min_depth_value)

                # min_depth_value = (1+0.001*math.pow(horizontal_distance,3))*min_depth_value


                # Print the depth value and coordinates
                print("Minimum depth value:", min_depth_value)
                # print("Coordinates (row, col):", min_depth_row, min_depth_col)
                print("Horizontal distance:", horizontal_distance)

                if depth_array.size != 0:
                    # if im is None:
                    #     # im_before = ax_before.imshow(before, cmap='viridis')
                    #     # ax_before.set_title('Original Depth Map')
                    #     # plt.colorbar(im_before, ax=ax_before, label='Depth (meters)')

                    #     # im = ax_after.imshow(depth_array, cmap='viridis')
                    #     # ax_after.set_title('Processed Depth Map')
                    #     # plt.colorbar(im, ax=ax_after, label='Depth (meters)')
                    #     continue

                    #     # ax_before.set_xlabel('Width (pixels)')
                    #     # ax_before.set_ylabel('Height (pixels)')
                    #     # ax_after.set_xlabel('Width (pixels)')
                    #     # ax_after.set_ylabel('Height (pixels)')
                    # else:
                    #     # im_before.set_data(before)
                    #     # im.set_data(depth_array)
                    #     # # ax_before.draw_artist(ax_before.patch)
                    #     # # ax_before.draw_artist(im_before)
                    #     # ax_after.draw_artist(ax_after.patch)
                    #     # ax_after.draw_artist(im)
                    #     # # fig_before.canvas.flush_events()
                    #     # fig_after.canvas.flush_events()
                    #     continue

                    # plt.pause(0.1)
                    continue
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
    depth_file_path = "/tmp/depth_data.npy"
    
    visualize_depth_data(depth_file_path)
    
