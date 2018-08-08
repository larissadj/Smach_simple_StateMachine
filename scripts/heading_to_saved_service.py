#!/usr/bin/env python

"""
## ------- IMPORTANT NOTE -------------##
## This can be Improved by using a Closed loop control system to reduce error
"""

import rospy
from std_srvs.srv import Empty,EmptyResponse
from std_msgs.msg import Float64
from mavros_msgs.msg import OverrideRCIn


# This class to get the latest hdg in the /mavros/global_position/compass_hdg
class hdg_tools(object):
    def __init__(self):
        self.init_hdg()
        self.init_saved_hdg()
        self.hdg_subscriber = rospy.Subscriber("/mavros/global_position/compass_hdg",Float64,
                                               self.hdg_callback,queue_size=1)
        self.save_subscriber = rospy.Subscriber("/autonomous/saved_heading", Float64,
                                                self.saved_callback,queue_size=10)
    def init_hdg(self):
        self._hdg = None
        while self._hdg is None:
            try:
                self._hdg = rospy.wait_for_message("/mavros/global_position/compass_hdg",
                                                   Float64, timeout=1)
            except:
                rospy.loginfo("/compass_hdg topic is not ready yet, retrying")

        rospy.loginfo("/compass_hdg topic READY")

    def init_saved_hdg(self):
        self._hdg = None
        while self._hdg is None:
            try:
                self._hdg = rospy.wait_for_message("/autonomous/saved_heading",
                                                   Float64, timeout=1)
            except:
                rospy.loginfo("/saved_heading topic is not ready yet, retrying")

        rospy.loginfo("/save_heading topic READY")


    def hdg_callback(self, msg):
        self._heading = msg
    def get_current_hdg(self):
        return self._heading.data

    def saved_callback(self, msg):
        self._saved_heading = msg
    def get_saved_heading (self):
        return self._saved_heading.data

class heading_accurate_movement (object):

    def __init__(self):
        self.hdg_tools_object = hdg_tools()
        self.rc_publisher = rospy.Publisher('/mavros/rc/override', OverrideRCIn,
                                            queue_size=10)
        self.service_server_object = rospy.Service('/autonomous/heading_to_saved',
                                                   Empty, self.service_callback)
        rospy.loginfo("The heading_to service is ready ")
        self.rate = rospy.Rate (10)


    def service_callback(self, req):
        current_heading = self.hdg_tools_object.get_current_hdg()
        goal_heading = self.hdg_tools_object.get_saved_heading()
        direction = self.shortest_path(goal_heading)
        override_msg = OverrideRCIn()
        if direction == 'r': #rotating to the Right
        #using the 4th cannel and a value above 1500
        #rospy.loginfo("the current heading is {}",format(current_heading))
            while (int(current_heading) != int(goal_heading)):
                override_msg.channels[3] = 1505
                self.rc_publisher.publish(override_msg)
                current_heading = self.hdg_tools_object.get_current_hdg()
                rospy.loginfo("Rotating to the right")

            rospy.loginfo("Stopped rotating heading reached")
            print("current heading :{}", format(current_heading))
            override_msg.channels[3] = 1500
            self.rc_publisher.publish(override_msg)
            return True
        elif direction == 'l':  #rotating to the left
        # using the 4 channel and value below 1500
            while (int(current_heading) != int(goal_heading)):
                override_msg.channels[3] = 1495
                self.rc_publisher.publish(override_msg)
                current_heading = self.hdg_tools_object.get_current_hdg()
                rospy.loginfo("rotating to the left")

            rospy.loginfo("stopped rotating heading reached")
            override_msg.channels[3] = 1500
            self.rc_publisher.publish(override_msg)
            return True
        else:
            rospy.logerr("The service did not work properly something went wrong")
            return False
    def shortest_path(self, goal_hdg):
        current_heading = self.hdg_tools_object.get_current_hdg()

        if current_heading > goal_hdg:
            return 'r'
        elif current_heading < goal_hdg:
            return 'l'
        else:
            rospy.logerr("The goal heading value is not correct")
            rospy.logerr("The value should be between 0 - 360 or -1 ")

if __name__ == '__main__':
    rospy.init_node('heading_to_savedserviceServer')
    object__ = heading_accurate_movement()
    rospy.spin()
