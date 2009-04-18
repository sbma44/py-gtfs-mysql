#!/usr/bin/python

import sys
import MySQLdb
import settings

trips = {}

def build_trip_scheme(cursor, service_id):

    trip_headsigns = {}
    
    print 'finding trips'
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
        
        trips[int(row[0])] = row[1]
    
    i = 0
    for trip_id in trips:
        print 'building stops for %s (%d of %d)' % (trips[trip_id], i, len(trips))

        trips[trip_id] = []
        
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
                
            trips[trip_id].append({
                'stop_id': row[0],
                'stop_lat': row[1],
                'stop_lon': row[2],
                'arrival_time_seconds': row[3],
                'departure_time_seconds': row[4]
            })
        
        i = i + 1


    


def setup_trip_bounds(cursor, service_id):    
    """
    creates and populates temporary tables for locating eligible trips
    """



    temp_sql = """
    DROP TABLE IF EXISTS trips_cached;
    CREATE TABLE trips_cached LIKE trips;
    INSERT INTO trips_cached SELECT * FROM trips WHERE service_id=%d;
    """ % service_id
    cursor.execute(temp_sql)
    
    temp_sql = """
    DROP TABLE IF EXISTS stop_times_cached;
    CREATE TABLE IF EXISTS stop_times_cached LIKE stop_times;
    INSERT INTO stop_times_cached SELECT * FROM stop_times st LEFT JOIN trips t ON st.trip_id=t.trip_id WHERE t.service_id=%d;
    """ % service_id
    cursor.execute(temp_sql)


def snapshot(cursor, service_id, second):    
    
    bus_locations = []
    
    # find all trips that are currently at a stop and record the stop locations (SET A - to be included in output)
    sql = """ 
    SELECT 
        s.stop_id,
        s.stop_lat, 
        s.stop_lon 
   
    FROM 
        stop_times_cached st 
    INNER JOIN 
        stops s ON s.stop_id=st.stop_id     
    INNER JOIN 
        trips_cached t ON t.trip_id=st.trip_id 
    
    WHERE 
        st.arrival_time_seconds<=%d 
    AND 
        st.departure_time_seconds>=%d
    
    """ % (second, second, service_id)

    cursor.execute(sql)

    while True:
        row = cursor.fetchone()
        if row is None:
            break
        
        bus_locations.append({
            'last_stop_id': row[0],
            'next_stop_id': row[0],
            'latitude': row[1],
            'longitude': row[2]
        })       

    
    # find all buses that are between two stops
    
    # - find stops that the bus has left

    sql = """
    SELECT 
        s.stop_lat,
        s.stop_lon,
        MAX(st.departure_time_seconds),
        s.stop_id,
        t.trip_id
        
    FROM        
        stop_times_cached st 
    INNER JOIN 
        stops s ON s.stop_id=st.stop_id     
    INNER JOIN 
        trips_cached t ON t.trip_id=st.trip_id 

    WHERE 
        st.departure_time<=%d 
        
    GROUP BY
        t.trip_id
        
    ORDER BY
        st.departure_time DESC,
        st.trip_id DESC
    """ % (second, service_id)
    cursor.execute(sql)
    
    trips = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        
        # is this an earlier departure on a previously recorded-trip? 
        trip_id = int(row[4])
        if trip_id not in trips:
            pass
        
        
        
    
    # for each trip in SET B, interpolate position based on last departure location, next arrival location & associated times
    
    # output set A and B
    
    cursor.close()
    
    
    
    


if __name__ == '__main__':
    conn = MySQLdb.connect (host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWORD, db=settings.MYSQL_DATABASE)
    cursor = conn.cursor()    
    
    # if '--build-cache' in sys.argv:
    #     setup_trip_bounds(conn)
    
    SERVICE_ID = 6 # weekday service occurring after 3/29/2009
    
    build_trip_scheme(cursor, SERVICE_ID)
    
    for s in range(0, 24*60*60):
        snapshot(cursor=cursor, service_id=SERVICE_ID, second=s)
        
    cursor.close()
    conn.close()