

class Lap:
    def __init__(self, frame, lap_time):
        self.lap = 0
        self.frame = frame
        self.lap_time = lap_time
        self.fuel = 0
        self.tire = 0

    def toJson(self):
        return {
            "lap": f"{self.lap}",
            "frame": f"{self.frame}",
            "lap_time": self.lap_time,
            "fuel": f"{self.fuel}",
            "tire": f"{self.tire}"
        }


class Laps:
    def __init__(self, laps):
        self.laps = laps

    def get_lap_times(self):
        return map(lambda x: x.lap_time, self.laps)

    def get_lap_frames(self):
        return map(lambda x: x.frame, self.laps)

    def get_lap_fuel(self):
        return map(lambda x: x.fuel, self.laps)

    def toJson(self):
        return map(lambda x: x.toJson(), self.laps)

    def to_lap_object(self, lap, object):
        if not lap.lap_time in object:
            object[lap.lap_time] = lap.toJson()

    def to_laps_object(self):
        laps_object = {}
        for i in range(len(self.laps)):
            self.to_lap_object(self.laps[i], laps_object)
        print(laps_object)
        return laps_object
