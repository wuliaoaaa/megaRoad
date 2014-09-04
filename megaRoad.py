#!/usr/bin/python
#coding=utf-8
import ConfigParser
import pdb
import json
class MegaRoad:

    def __init__(self, config_file):
        """ """

        # the map of lines of station 
        self.lines = []
        # the transfer station of each line
        self.line_connections = []
        # line graph 
        self.line_graph = []
        # the line no to line name
        self.no_name = []
        self.init_lines(config_file)
        self.init_line_connections()
        self.init_line_graph()

    def print_list(l):
        """print the list"""

        for item in l:
            print item

    def init_line_connections(self):
        """init line connections"""

        station_line = dict()

        for line in xrange(len(self.lines)):
            for station in self.lines[line]:
                if station_line.get(station, []) == []:
                    station_line[station] = [line] 
                else:
                    station_line[station].append(line)

        for i in xrange(len(self.lines)):
            temp = dict()
            self.line_connections.append(temp)

        for station, line_list in station_line.items():
            if len(line_list) > 1:
                for stay_line in line_list:
                    for transfer_line in line_list:
                        if stay_line != transfer_line:
                            self.line_connections[stay_line][transfer_line] = station


    def init_lines(self, file_path):
        """init lines"""

        config = ConfigParser.ConfigParser()
        config.read(file_path)
        options = config.options("default")
        
        for option in options:
            self.no_name.append(option)
            line = config.get("default", option)
            self.lines.append(line.split(","))

    def init_line_graph(self):
        """ """
        for line_no in xrange(len(self.lines)):
            line_connections_inf = self.line_connections[line_no]
            line_inf = self.lines[line_no]
            line_station_map = dict()
            for line, station in line_connections_inf.items():
                for line2, station2 in line_connections_inf.items():
                    if line != line2:
                        station_index = line_inf.index(station)
                        station2_index = line_inf.index(station2)
                        line_station_map.update({'-'.join([str(line),
                            str(line2)]):
                            abs(station_index - station2_index)})
            self.line_graph.append(line_station_map)



    def modify_line_graph(self, start_station, line_no):
        """modify the line's weight"""
        
        modify_line_graph = list(self.line_graph)
        line_station_map = dict()
        line_connection_inf = self.line_connections[line_no]
        line_inf = self.lines[line_no]
        start_station_index = line_inf.index(start_station)
        for line, station in line_connection_inf.items():
            station_index = line_inf.index(station)
            line_station_map.update({'-'.join([str(line_no),str(line)]):abs(start_station_index-station_index)})

        modify_line_graph[line_no]=line_station_map
        return modify_line_graph




    def dijkstra(self, start_line, end_line, line_graph):
        """find the transfer lines from start station to end station"""

        path = [0 for i in xrange(len(self.lines))]
        current_paths = list() 
        current_paths.append([start_line, 0])
        path[start_line] = start_line

        remain_lines = set()
        for i in xrange(len(self.lines)):
            remain_lines.add(i)
        remain_lines.remove(start_line)

        min_weight = 10000
        while True:
            min_node = start_line
            min_node_pre = start_line 
            min_weight = 10000

            for current_line,current_weight in current_paths:
                pre_line = path[current_line]
                for line,station in self.line_connections[current_line].items():
                    if line in remain_lines:
                        line_pair = '-'.join([str(pre_line), str(line)])
                        weight = line_graph[current_line].get(line_pair, -1)
                        if weight+current_weight < min_weight:
                            min_node = line
                            min_node_pre = current_line
                            min_weight = weight + current_weight

            current_paths.append([min_node, min_weight])

            print min_node
            remain_lines.remove(min_node)

            path[min_node] = min_node_pre
            if min_node == end_line:
                break

        result = list()
        cur_node = end_line
        result.append(cur_node)
        while cur_node != start_line:
            cur_node = path[cur_node]
            result.append(cur_node)
        result.reverse()
        return result

    def get_line_stations(self, begin_station, end_station, line_no):
        """ get the route from start station to end station"""
        stations_to_walk = ""
        line_information = self.lines[line_no]
        begin_station_index = line_information.index(begin_station)
        end_station_index = line_information.index(end_station)
        if  begin_station_index < end_station_index:
            stations_to_walk = ",".join(line_information[begin_station_index:end_station_index+1])
        else:
            temp = line_information[end_station_index:begin_station_index+1]
            temp.reverse()
            stations_to_walk = ','.join(temp)

        return stations_to_walk

    def get_station_line(self, station):
        """" lines which the station in """
        for i in xrange(len(self.lines)):
            try:
                self.lines[i].index(station)
                return i
            except ValueError:
                pass
        return None 

    def get_route(self, start_station, end_station):
        """ compute the rout from start station to end station """

        result = list()
        start_station_line = self.get_station_line(start_station)
        end_station_line = self.get_station_line(end_station)
        modify_line_graph = self.modify_line_graph(start_station,
                start_station_line)
        path = self.dijkstra(start_station_line, end_station_line,
                modify_line_graph)


        i = 0 
        line_begin_station = start_station
        line_result_template = "line {lineNum}: {stations} "
        while i < len(path)-1:
            cur_line = path[i]
            i = i + 1
            next_line = path[i]
            line_connection_info = self.line_connections[cur_line]
            line_end_station = line_connection_info[next_line]
            
            stations_to_walk = self.get_line_stations(line_begin_station, line_end_station, cur_line) 
            result.append(line_result_template.format(lineNum=cur_line,
                stations=stations_to_walk))

            line_begin_station = line_end_station

        
        cur_line = path[i]
        stations_to_walk = self.get_line_stations(line_begin_station,
                end_station, cur_line) 
        result.append(line_result_template.format(lineNum=self.no_name[cur_line],
            stations=stations_to_walk))

        return '\n'.join(result)

    def exist_station(self, station):
        """determint whether the station exist or not """
        for line in self.lines:
            for element in line:
                if element == station:
                    return True
        return False

if __name__ == "__main__":
    mega = MegaRoad("config")

    while True:
        start_station = raw_input("Input the start station:")
        end_station = raw_input("Input the end station:")
        #start_station = "瀹㈡潙"
        #end_station = "涓囪儨鍥�"
        if mega.exist_station(start_station) and mega.exist_station(end_station):
            route = mega.get_route(start_station, end_station)
            print route
        else:
            print "no such station"




