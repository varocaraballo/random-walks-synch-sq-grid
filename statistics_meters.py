# -*- coding: utf-8 -*-

class ArcCoveringStatistics(object):
    def __init__(self, keepData=False):
        self.last_visit = -1
        self.max_idle = -1
        self.min_idle = float('inf')
        self.avg_idle = float('inf')
        self.visits_count = 0
        self.total_idle = 0
        if keepData:
            self.data = {}
        
    def visit(self, number_iter):
        assert number_iter >= self.last_visit
        if self.last_visit != number_iter:
            self.visits_count += 1
            if self.last_visit != -1:
                t = number_iter - self.last_visit
                if hasattr(self,'data'):
                    self.data.setdefault(t,0)
                    self.data[t] += 1
                self.total_idle +=t
                self.max_idle = max(t, self.max_idle)
                self.min_idle = min(t, self.min_idle)
                self.avg_idle = self.total_idle/self.visits_count
        self.last_visit = number_iter
        
        
class TokenStatistics(object):
    def __init__(self, creation_iter, creator, k, knowers=None):
        self.creation_iter = creation_iter
        self.creator = creator
        self.knowers = set() if knowers is None else knowers
        self.knowers.add(creator)
        self.broad_cast_time = float('inf') if len(self.knowers)<k else 0
        
    def isBroadCasted(self, k, number_iter, involve_drones):
        if len(self.knowers) == k:
            return self.broad_cast_time
        if len(self.knowers.intersection(involve_drones))>0:
            self.knowers.update(involve_drones)
            if len(self.knowers) == k:
                self.broad_cast_time = number_iter - self.creation_iter 
                return self.broad_cast_time
        return None
        
            
class DroneStatistics(object):
    def __init__(self):
        self.last_meeting = -1
        self.max_isolation = -1
        self.min_isolation = float('inf')
        self.avg_isolation = float('inf')
        self.meetings_count = -1
        self.total_isolation = 0
        self.last_neighbors = {}
        
    def meeting(self, number_iter, neighbors):
        if self.last_meeting != number_iter:
            if self.last_meeting == -1:
                self.meetings_count += 1
            else:
                if number_iter-1 != self.last_meeting or len(self.last_neighbors.intersection(neighbors))==0:
                    self.meetings_count += 1
                    t = number_iter - self.last_meeting
                    self.total_isolation += t
                    self.max_isolation = max(t, self.max_isolation)
                    self.min_isolation = min(t, self.min_isolation)
                    self.avg_isolation = self.total_isolation/self.meetings_count
                
        self.last_meeting = number_iter
        self.last_neighbors = neighbors