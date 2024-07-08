

# UAV project

## This project assumes that you are working on Ubuntu 20.04

# Build required SDK's
[Ardupilot](https://docs.google.com/document/d/1ihAxgX1y3yRMqRnX1yWfk9WDaxZt8JmtFyEddi13SWw/edit)

[Realsense SDK](https://www.mouser.com/applications/getting-started-with-realsense-d455/)

# Tutorial of current algorithms
+ Clone this repo in src folder of catkin_ws
+ get [runway4.world](https://drive.google.com/file/d/1wEHAJMRoC_oQrESQtgkyWg47hVZCOi0y/view?usp=sharing) and add it to your worlds folder in iq_sim
+ change [runway.launch](https://drive.google.com/file/d/1GZMbl0JDaDLkVXpZpK9obQmARWhDPD52/view?usp=sharing) file in launch folder in iq_sim to run runway4.world
+ Open a terminal and run the following scripts parallelly   

  

      cd catkin_ws/
      cd src
      cd iq_sim
      roslaunch iq_sim runway.launch
      roslaunch iq_sim apm.launch
        
    This will start the Gzebo world and initialize the ros nodes.
    Now run the startsitl.sh file in **new terminal**

		cd ~
        ./startsitl.sh
Now run the python scripts in src **each in new terminal**

    python ros_script.py
    python ros_front.py
    python f2.py
    python down.py


Now in SITL set the mode to guided and takeoff

    mode guided
    arm throttle
    takeoff 10

Now run the altmaintain11.py script in src

    python altmaintain11.py


    
[Screencast from 08-07-24 03:21:10 PM IST.webm](https://github.com/codemaster1104/UAV/assets/115527374/7340066e-d0f3-4b90-83c0-3dbc77585eac)


# Overview of algorithm
The drone has 2 realsense depth cameras attached to it in this simulation

Processing downward depth data is fairly easy we are looking for the hieghest tree and its position by searching for the lowest depth pixel value and its position in image

For front facing camera we are forming a terrain map by using a simple edge detection algorithm
![Screenshot from Screencast from 17-06-24 03:25:06 PM IST webm](https://github.com/codemaster1104/UAV/assets/115527374/cb831b4e-7631-4bda-91c0-c376d4c5a3de)

Once we have data from front and downward facing camera alt_maintain11.py performs decision making for which feed to prioritise and adjusts the z velocity of drone accordingly
