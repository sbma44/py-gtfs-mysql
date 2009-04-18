#!/usr/bin/python

import sys
import MySQLdb
import pickle
import os
from decimal import Decimal

trips = {}
trip_bounds = {}

class GTFSSnapshotCalculator(object):

    def __init__(self, service_id):
        super(GTFSSnapshotCalculator, self).__init__()

        self.trips = {}
        self.trip_bounds = {}
        self.service_id = service_id

        self.build_trip_schemes(self.service_id)
        

    def build_trip_schemes(self, service_id):

        import settings

        TRIPS_PICKLE_FILE = 'trips.%d.pickle' % service_id
        TRIP_BOUNDS_PICKLE_FILE = 'trip_bounds.%d.pickle' % service_id

        if os.path.exists(TRIPS_PICKLE_FILE):
            print 'loading trip sequences from file'
            f = open(TRIPS_PICKLE_FILE, 'r')
            self.trips = pickle.load(f)
            f.close()        

        else:

            trip_headsigns = {}
                        
            print 'building trip sequences'
            
            conn = MySQLdb.connect (host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWORD, db=settings.MYSQL_DATABASE)
            cursor = conn.cursor()            
            
            sql = """ 
            SELECT
                trip_id, trip_headsign 
            FROM 
                trips t
            WHERE 
                t.service_id=%d
            ORDER BY
                t.trip_id ASC
            """ % service_id
    
            cursor.execute(sql.replace("\n", " "))
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
        
                self.trips[int(row[0])] = row[1]

            padding = len(str(len(self.trips)))
            i = 0
            for trip_id in self.trips:
                print '%s/%s %s' % (str(i).zfill(padding), str(len(self.trips)).zfill(padding), self.trips[trip_id])

                self.trips[trip_id] = []
        
                sql = """
                SELECT 
                    s.stop_id,
                    s.stop_lat,
                    s.stop_lon,
                    st.arrival_time_seconds,
                    st.departure_time_seconds
        
                FROM
                    stop_times st
                        INNER JOIN 
                            stops s
                                ON s.stop_id=st.stop_id
          
                WHERE
                    st.trip_id=%d
            
                ORDER BY
                    st.stop_sequence ASC
        
                """ % trip_id
        
                cursor.execute(sql.replace("\n", " "))
                while True:
                    row = cursor.fetchone()
                    if row is None:
                        break
                
                    self.trips[trip_id].append({
                        'stop_id': row[0],
                        'stop_lat': row[1],
                        'stop_lon': row[2],
                        'arrival_time_seconds': row[3],
                        'departure_time_seconds': row[4]
                    })
        
                i = i + 1
        
            print 'saving trip sequences to file'
            f = open(TRIPS_PICKLE_FILE, 'w')
            pickle.dump(self.trips, f)
            f.close()
            
            cursor.close()
            conn.close()

        if os.path.exists(TRIP_BOUNDS_PICKLE_FILE):
            print 'loading stop time bounds from file'
            f = open(TRIP_BOUNDS_PICKLE_FILE, 'r')
            self.trip_bounds = pickle.load(f)
            f.close()
        else:
            print 'building stop time bounds'
            
            conn = MySQLdb.connect (host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWORD, db=settings.MYSQL_DATABASE)
            cursor = conn.cursor()            
            
            for trip_id in self.trips:
                self.trip_bounds[trip_id] = (self.trips[trip_id][0]['arrival_time_seconds'], self.trips[trip_id][-1]['departure_time_seconds'])
            print 'saving stop time bounds to file'
            f = open(TRIP_BOUNDS_PICKLE_FILE, 'w')
            pickle.dump(self.trip_bounds, f)
            f.close()
            
            cursor.close()
            conn.close()
           
    def snapshot(self, second):    

        bus_locations = []

        for trip_id in self.trip_bounds:
            if second>=self.trip_bounds[trip_id][0] and second<=self.trip_bounds[trip_id][1]:
                for stop_i in xrange(0,len(self.trips[trip_id])):
                    # is the bus at a stop right now?
                    if second>=self.trips[trip_id][stop_i]['arrival_time_seconds'] and second<=self.trips[trip_id][stop_i]['departure_time_seconds']:
                        bus_locations.append( (self.trips[trip_id][stop_i]['stop_id'], self.trips[trip_id][stop_i]['stop_id'], self.trips[trip_id][stop_i]['stop_lat'], self.trips[trip_id][stop_i]['stop_lon'], 'AT STOP') )
                        break

                    # is it between stops?
                    if stop_i<(len(self.trips[trip_id]) - 1):
                        if second>self.trips[trip_id][stop_i]['departure_time_seconds'] and second<self.trips[trip_id][stop_i+1]['arrival_time_seconds']:
                            # interpolate lat/lon for two stops
                            start = self.trips[trip_id][stop_i]
                            end = self.trips[trip_id][stop_i+1]
                            start_weight = Decimal(str((second - start['departure_time_seconds']) / (1.0 * end['arrival_time_seconds'] - start['departure_time_seconds'])))
                            lat = (start['stop_lat'] * start_weight) + (end['stop_lat'] * (Decimal('1.0') - start_weight))
                            lon = (start['stop_lon'] * start_weight) + (end['stop_lon'] * (Decimal('1.0') - start_weight))

                            bus_locations.append( (start['stop_id'], end['stop_id'], lat, lon, 'IN TRANSIT') )

        return bus_locations
        
        

if __name__ == '__main__':
    
    SERVICE_ID = 6
    SC = GTFSSnapshotCalculator(SERVICE_ID)
    for s in range(0, 24*60*60):
        SC.snapshot(second=s)
    