import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import os

class DepthCameraSubscriber:
    def __init__(self):
        # Initialize the ROS node
        rospy.init_node('depth_camera_subscriber', anonymous=True)
        
        # Create a CvBridge object to convert ROS Image messages to OpenCV images
        self.bridge = CvBridge()
        
        # Subscribe to the depth image topic
        self.subscriber = rospy.Subscriber('/depth_camera/depth/image_raw', Image, self.depth_callback)
        
        # Path to save depth data
        self.depth_file_path = "/tmp/front_depth_data.npy"

    def depth_callback(self, msg):
        try:
            # Convert the ROS Image message to a NumPy array
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            depth_array = np.array(depth_image, dtype=np.float32)

            # Save the depth array to a file
            np.save(self.depth_file_path, depth_array)

        except CvBridgeError as e:
            rospy.logerr("Error converting depth image: %s", str(e))

if __name__ == '__main__':
    try:
        # Create an instance of the DepthCameraSubscriber class
        subscriber = DepthCameraSubscriber()
        
        # Keep the node running until it's stopped
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

