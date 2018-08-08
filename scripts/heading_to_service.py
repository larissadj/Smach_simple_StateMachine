#!/usr/bin/env python

## ------- IMPORTANT NOTE -------------##
## This can be Improved by using a Closed loop control system to reduce error


import rospy
from smach_mavros_ardusub_test.srv import hdg, hdgResponse
from std_msgs.msg import Float64
from mavros_msgs.msg import OverrideRCIn


# This class to get the latest hdg in the /mavros/global_position/compass_hdg
class hdg_tools(object):
    def __init__(self):
        self.init_hdg()
        self.hdg_subscriber = rospy.Subscriber("/mavros/global_position/compass_hdg",Float64,
                                               self.hdg_callback,queue_size=1)
    def init_hdg(self):
        self._hdg = None
        while self._hdg is None:
            try:
                self._hdg = rospy.wait_for_message("/mavros/global_position/compass_hdg",
                                                   Float64, timeout=1)
            except:
                rospy.loginfo("/compass_hdg topic is not ready yet, retrying")

        rospy.loginfo("/compass_hdg topic READY")

    def hdg_callback(self, msg):
        self._heading = msg
    def get_current_hdg(self):
        return self._heading.data

class heading_accurate_movement (object):

    def __init__(self):
        self.hdg_tools_object = hdg_tools()
        self.rc_publisher = rospy.Publisher('/mavros/rc/override', OverrideRCIn,
                                            queue_size=10)
        self.service_server_object = rospy.Service('/autonomous/heading_to',
                                                   hdg, self.service_callback)
        rospy.loginfo("The heading_to service is ready ")
        self.rate = rospy.Rate (10)


    def service_callback(self, req):
        goal_heading = req.desired_hdg
        current_heading = self.hdg_tools_object.get_current_hdg()
        direction = self.shortest_path(goal_heading)
        override_msg = OverrideRCIn()
        if direction == 'r': #rotating to the Right
        #using the 4th cannel and a value above 1500
        #rospy.loginfo("the current heading is {}",format(current_heading))
            rospy.loginfo("Rotating to the right")
            while (int(current_heading) != int(goal_heading)):
                override_msg.channels[3] = 1550
                self.rc_publisher.publish(override_msg)
                self.rate.sleep()
                current_heading = self.hdg_tools_object.get_current_hdg()
            override_msg.channels[3] = 1500
            self.rc_publisher.publish(override_msg)
            self.rate.sleep()
            rospy.loginfo("Stopped rotating heading reached : %f",current_heading)
            return True
        elif direction == 'l':  #rotating to the left
        # using the 4 channel and value below 1500
            rospy.loginfo("rotating to the left")
            while (int(current_heading) != int(goal_heading)):
                override_msg.channels[3] = 1450
                self.rc_publisher.publish(override_msg)
                self.rate.sleep()
                current_heading = self.hdg_tools_object.get_current_hdg()

            override_msg.channels[3] = 1500
            self.rc_publisher.publish(override_msg)
            self.rate.sleep()
            rospy.loginfo("Stopped rotating heading reached : %f",current_heading)
            return True
        else:
            rospy.logerr("The service did not work properly something went wrong")
            return False
    def shortest_path(self, goal_hdg):
        current_heading = self.hdg_tools_object.get_current_hdg()
        # To calculate the shortest path I divided the heading into 4 quarters and the
        #Algorithm as following
        if current_heading > goal_hdg:
            if 1 < goal_hdg < 90:
                return 'r'
            else:
                return 'l'
        elif current_heading < goal_hdg:
            if  270 < goal_hdg < 359:
                return 'l'
            else:
                return 'r'
        else:
            rospy.logerr("The goal heading value is not correct")
            rospy.logerr("The value should be between 0 - 360 or -1 ")

if __name__ == '__main__':
    rospy.init_node('heading_to_serviceServer')
    object__ = heading_accurate_movement()
    rospy.spin()
