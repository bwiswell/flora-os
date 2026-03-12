"""
slam
==========
Python implementation of Occupancy-SLAM.

Attribution:
    Paper: Occupancy-SLAM: An Efficient and Robust Algorithm...
    Authors: Yingyu Wang, Liang Zhao, Shoudong Huang
    Link: https://arxiv.org

This module uses or takes inspiration from the following additional sources:
- [Federico Sarrocco] (https://federicosarrocco.com/blog/graph-slam-tutorial):
    An incredible how-to for GraphSLAM techniques used for guidance.
"""

from .slam_builder import SLAMBuilder