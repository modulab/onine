#!/usr/bin/env python
import os, sys, rospy, tf, actionlib, moveit_commander
from control_msgs.msg import (GripperCommandAction, GripperCommandGoal)
from geometry_msgs.msg import *
from tf.transformations import quaternion_from_euler, euler_from_quaternion
from moveit_commander import RobotCommander, PlanningSceneInterface
from moveit_msgs.msg import PickupAction, PickupGoal

import time
import math

class Onine():

    def __init__(self, arm_group):
        self.arm_group = arm_group
        self.tf_listener = tf.TransformListener() 
        self.p = Pose()

    def goto(self, x, y, z, yaw):
        self.p.position.x = x
        self.p.position.y = y
        self.p.position.z = z
        self.p.orientation = Quaternion(*quaternion_from_euler(-1.55961170956, 0.00000, yaw))
        self.arm_group.set_pose_target(self.p)
        # plan1 = self.arm_group.plan()
        # self.arm_group.execute(plan1)
        os.system("rosservice call clear_octomap")
        self.arm_group.go(wait=True)


    def get_grasp_pose(self, x, y, z, distance):
        origin_translation = [0.095, 0.00, 0.00]

        delta_x = x - origin_translation[0]
        delta_y = y - origin_translation[1]

        if(y > 0):
            theta = math.atan(delta_x / delta_y)
            grasp_yaw = -1.00 * theta
            grasp_x = x - (distance * math.sin(grasp_yaw))
            grasp_y = y + (distance * math.cos(grasp_yaw))

        elif(y < 0):
            theta = math.atan(delta_x / delta_y)
            grasp_yaw = -1.00 * ((math.pi / 2.00) - theta)
            grasp_x = x - (distance * math.sin(theta))
            grasp_y = y - (distance * math.cos(theta))

        return (grasp_x, grasp_y, z, grasp_yaw)

    def ready(self):
        self.arm_group.set_named_target("onine_ready")
        self.arm_group.go(wait=True)
        os.system("rosservice call clear_octomap")

    def open_gripper(self):
        os.system("rostopic pub /onine_gripper std_msgs/Bool 1 -1")

    def close_gripper(self):
        os.system("rostopic pub /onine_gripper std_msgs/Bool 0 -1")

    def pickup(self, x, y, z):
        self.ready()
        self.open_gripper()
        (aim_x, aim_y, aim_z, aim_yaw) = self.get_grasp_pose(x, y, z, -0.10)
        self.goto(aim_x, aim_y, aim_z, aim_yaw)
        print aim_x
        print aim_y
        print aim_z
        print aim_yaw
        self.goto(x, y, z, aim_yaw)
        self.close_gripper()

if __name__ == '__main__':
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('pick_up_item')

    arm_group = moveit_commander.MoveGroupCommander("onine_arm") 
    arm_group.allow_replanning(True)
    rate = rospy.Rate(10)

    tf_listener = tf.TransformListener() 

    scene = PlanningSceneInterface()
    robot = moveit_commander.RobotCommander()
    rospy.sleep(2)

    while not rospy.is_shutdown():
        rate.sleep()

        # try:
        #   t = tf_listener.getLatestCommonTime('/base_footprint', '/ar_marker_3') # <7>
        #   if (rospy.Time.now() - t).to_sec() > 0.2:
        #     continue

        #   (item_translation, item_orientation) = tf_listener.lookupTransform('/base_footprint', "ar_marker_3", t) 
        # except(tf.Exception, tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        #     continue

        #left test
        # yaw = -0.949421004148
        item_translation = [0.33292386367734217, 0.1685605027519197, 0.8339949674141176]
        
        #right test
        # yaw =  -2.33954420079
        # item_translation = [0.3155979994864394, -0.21095350748804098, 0.8829674860024487]

        # p = PoseStamped()
        # p.header.frame_id = robot.get_planning_frame()
        # p.pose.position.x = item_translation[0]
        # p.pose.position.y = item_translation[1]
        # p.pose.position.z = item_translation[2]
        # scene.add_box("target", p, (0.06, 0.06, 0.09))

        # arm_group.set_goal_tolerance(0.001)
        arm_group.set_goal_position_tolerance(0.005)
        arm_group.set_goal_orientation_tolerance(0.1)
        arm_group.set_num_planning_attempts(30)
        arm_group.set_planning_time(15)
        arm_group.set_planner_id("RRTkConfigDefault")

        onine_arm = Onine(arm_group)

        onine_arm.pickup(item_translation[0], item_translation[1], item_translation[2])
        break 