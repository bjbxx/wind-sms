"""Kiteboard wind alert script
   Uses google chart API to display last 6 hours of wind data from folly beach
   Sends SMS message via SMTP if wind is up (currently > 13 mph)
"""

import urllib.request
import pytz
import notifier
import time
from pytz import timezone
from datetime import datetime, timedelta

# Google chart API URL
# Wind direction and time on x axis, y axis displays speed in mph
GOOGLE_CHART_API = "http://chart.googleapis.com/chart?chxp=1,0,1,2,3,4,5,6" + \
                   "|2,0,1,2,3,4,5,6&chxr=0,0,35.5|1,0,6|2,0,6&chxs=1," + \
                   "676767,11.5,0,lt,676767&chxt=y,x,x&chs=320x240&cht=lc" + \
                   "&chco=EC2416,FF9900&chds=0,35,-1,40&chg=16.66,-1,0,0" + \
                   "&chls=2|3&chma=0,0,0,5&chm=r,18FF2465,0,0.82,0.3&chxl="


def get_wind_direction(compass):
    """Converts a float from 0.0-360.0 to a plain english direction"""

    direction = ""

    if compass > 348.75 or compass <= 11.250:
        direction = 'N'
    elif compass > 11.250 and compass <= 33.750:
        direction = 'NNE'
    elif compass > 33.750 and compass <= 56.250:
        direction = 'NE'
    elif compass > 56.250 and compass <= 78.750:
        direction = 'ENE'
    elif compass > 78.750 and compass <= 101.25:
        direction = 'E'
    elif compass > 101.25 and compass <= 123.75:
        direction = 'ESE'
    elif compass > 123.75 and compass <= 146.25:
        direction = 'SE'
    elif compass > 146.25 and compass <= 168.75:
        direction = 'SSE'
    elif compass > 168.75 and compass <= 191.25:
        direction = 'S'
    elif compass > 191.25 and compass <= 213.75:
        direction = 'SSW'
    elif compass > 213.75 and compass <= 236.25:
        direction = 'SW'
    elif compass > 236.25 and compass <= 258.75:
        direction = 'WSW'
    elif compass > 258.75 and compass <= 281.25:
        direction = 'W'
    elif compass > 281.25 and compass <= 303.75:
        direction = 'WNW'
    elif compass > 303.75 and compass <= 326.25:
        direction = 'NW'
    elif compass > 326.25 and compass <= 348.75:
        direction = 'NNW'

    return direction

def build_google_url(data):
    """Converts data dict from a station runner into a google chart URL"""

    google_chart_url = ""

    if data and 'mph' in data:

        mph_list = data['mph']
        gust_list = data['gust']
        dir_list = data['wind_dir']
        time_list = data['time']

        if mph_list and gust_list and dir_list and time_list:

            # Reverse all arrays, due to how google parses data
            mph_list.reverse()
            gust_list.reverse()
            dir_list.reverse()
            time_list.reverse()

            google_chart_url = (GOOGLE_CHART_API + '1:|' + \
                                '|'.join(time_list) + '|2:|' + \
                                '|'.join(dir_list) + '&chd=t:'+ \
                                ','.join(mph_list) + '|' + \
                                ','.join(gust_list))

    return google_chart_url


class StationRunner(object):
    """Class used to build NOAA stations and run wind alerts"""

    def __init__(self, station_id, min_wind, is_cont=False):

        # URL from the national buoy data center for a given weather station
        self.noaa_url = "http://www.ndbc.noaa.gov/data/realtime2/" + \
                         station_id + ".cwind"

        self.chart_filename = station_id + '_chart.png'
        self.smtp_notify = notifier.SmtpNotifier()
        self.is_continuous = is_cont
        self.threshold = min_wind
        self.time_zone = timezone('US/Eastern')

        # Default last update to the previous hour
        self.last_update_dt = (datetime.now(tz=self.time_zone). \
                               replace(minute=0, second=0, microsecond=0) \
                               - timedelta(hours=1))

    def sleep_until_next_update(self):
        """Takes last update and sleeps until appropriate next update"""

        next_update = (datetime.now().replace(minute=15, second=0, microsecond=0) \
                       + timedelta(hours=1))

        # After 7 pm, sleep until 8 am
        # Make timezone aware to account for possible daylight savings
        if next_update.hour >= 20:

            print("Sleep until tomorrow")

            tomorrow = (datetime.now(tz=self.time_zone). \
                        replace(hour=8, minute=15, second=0, microsecond=0) \
                        + timedelta(days=1))

            # Set last update to the previous hour
            self.last_update_dt = (tomorrow - timedelta(hours=1))

            sleep_amount = tomorrow - datetime.now(tz=self.time_zone)
            time.sleep(sleep_amount.total_seconds())

        else:
            print("Sleep until next hour")
            time.sleep((next_update - datetime.now()).total_seconds())


    def get_data_dict(self, req_data):
        """Method which converts url request into a meaningful dictionary"""

        if not req_data:
            return []

        # Organize data into appropriate lists
        mph_list, gust_list, dir_list, time_list = [], [], [], []
        for line in req_data.splitlines():

            # NOAA cswind format below
            #YY  MM DD hh mm WDIR WSPD GDR GST GTIME
            #yr  mo dy hr mn degT m/s degT m/s hhmm
            if line.decode('utf-8').find('#') == -1:

                # Stop after 36 lines of data (6 per hour * 6 hours)
                if len(mph_list) > 36:
                    break

                data = line.decode('utf-8').split()

                try:
                    utc_dt = datetime(int(data[0]), \
                                      int(data[1]), \
                                      int(data[2]), \
                                      int(data[3]), \
                                      int(data[4]), \
                                      0, tzinfo=pytz.utc)

                    local_dt = utc_dt.astimezone(self.time_zone)

                except ValueError:
                    print("Unable to parse data - Invalid value!")
                    return []

                if not mph_list:

                    if local_dt <= self.last_update_dt:
                        print("No new data yet for current hour")
                        return []
                    else:
                        self.last_update_dt = local_dt
                        print("Gathering new data for " + \
                              local_dt.strftime('%Y-%m-%d %I:%M:%S %Z%z'))

                # Only record wind direction once every hour
                if len(mph_list) % 6 == 0:
                    time_list.append(local_dt.strftime('%I'))
                    dir_list.append(get_wind_direction(float(data[5])))

                # Wind speeds from NOAA are recorded as m/s - convert to MPH
                mph = round(float(data[6]) * 2.23693, 1)
                mph_list.append(str(mph))

                gust = float(data[8])
                if gust < 99:
                    gust = round(gust * 2.23693, 1)
                    gust_list.append(str(gust))

        return {'mph': mph_list, \
                'gust': gust_list, \
                'wind_dir': dir_list, \
                'time': time_list}

    def run(self):
        """Method which polls NOAA URL,
           sends wind alert if necessary,
           and sleeps until next update if running continuously
        """

        while True:
            # Read wind data from NOAA URL
            try:
                noaa_req = urllib.request.urlopen(self.noaa_url)
                req_data = noaa_req.read()
            except urllib.request.URLError:
                print("Unable to read NOAA URL")

                if not self.is_continuous:
                    break

                # Sleep 30 seconds and try again
                time.sleep(30)

            data = self.get_data_dict(req_data)
            if not data:

                if not self.is_continuous:
                    break

                # Sleep 5 minutes and try again
                time.sleep(300)

            chart_url = build_google_url(data)
            if chart_url:

                # Get latest wind speed and direction
                # Safe to pop since we are done with these lists
                cur_wind_dir = data['wind_dir'].pop()
                cur_wind_speed = data['mph'].pop()

                # If wind speed over threshold - send SMS alert
                print("Current mph: " + cur_wind_speed + " " + cur_wind_dir)

                if float(cur_wind_speed) >= self.threshold:

                    try:
                        chart_req = urllib.request.urlopen(chart_url)
                        data_file = open(self.chart_filename, 'wb')
                        data_file.write(chart_req.read())
                        data_file.close()
                    except urllib.request.URLError:
                        print("Unable to read chart data")
                    except IOError:
                        print("Unable to read/write latest chart data")

                    (self.smtp_notify. \
                     send('Currently ' + cur_wind_speed + \
                          ' mph ' + cur_wind_dir, self.chart_filename))

                if not self.is_continuous:
                    break

                self.sleep_until_next_update()
