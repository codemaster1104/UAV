#!/usr/bin/env python

import rospy
import tf
from sensor_msgs.msg import Imu

def imu_callback(data):
    # Extract quaternion from the message
    quaternion = (
        data.orientation.x,
        data.orientation.y,
        data.orientation.z,
        data.orientation.w
    )

    # Convert quaternion to Euler angles
    euler = tf.transformations.euler_from_quaternion(quaternion)

    # Print the Euler angles (Roll, Pitch, Yaw)
    roll, pitch, yaw = euler
    rospy.loginfo("Roll: %f, Pitch: %f, Yaw: %f", roll, pitch, yaw)

def imu_listener():
    # Initialize the ROS node
    rospy.init_node('imu_listener', anonymous=True)

    # Subscribe to the /mavros/imu/data topic
    rospy.Subscriber('/mavros/imu/data', Imu, imu_callback)

    # Keep the node running
    rospy.spin()

if __name__ == '__main__':
    imu_listener()
