""" Module used to send a message and png image to a cell phone """

import windsms

# Build Folly Beach station and run continuously
windsms.StationRunner(station_id='FBIS1', min_wind=13, is_cont=True).run()