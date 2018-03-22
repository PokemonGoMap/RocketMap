from .utils import distance
from .transform import intermediate_point


class LocationCluster(object):
    def __init__(self, location):
        self._locations = [location]
        self.centroid = self.get_position(location)

    def __getitem__(self, key):
        return self._locations[key]

    def __iter__(self):
        for x in self._locations:
            yield x

    def __contains__(self, item):
        return item in self._locations

    def __len__(self):
        return len(self._locations)

    def append(self, location):
        self.centroid = self.new_centroid(location)

        self._locations.append(location)

    def get_score(self, location, time_threshold=-1):
        position = self.get_position(location)
        return distance(position, self.centroid)

    # The finest Duck programming money can offer.
    @staticmethod
    def get_position(location):
        if 'lat' in location:
            position = (location['lat'], location['lng'])
        elif 'latitude' in location:
            position = (location['latitude'], location['longitude'])
        else:
            # Assume it's a tuple/list already.
            position = location
        return position

    def new_centroid(self, location):
        sp_count = len(self._locations)
        f = sp_count / (sp_count + 1.0)
        new_centroid = intermediate_point(
            self.get_position(location), self.centroid, f)

        return new_centroid

    def test_location(self, location, radius, time_threshold=-1):
        # Discard spawn points outside the time frame or too far away.
        if self.get_score(location, time_threshold) > 2 * radius:
            return False

        new_centroid = self.new_centroid(location)

        # Check if spawn point is within range of the new centroid.
        if (distance(self.get_position(location), new_centroid) >
                radius):
            return False

        # Check if cluster's spawn points remain in range of the new centroid.
        if any(distance(self.get_position(x), new_centroid) >
                radius for x in self._locations):
            return False

        return True


class SpawnCluster(LocationCluster):
    def __init__(self, spawnpoint):
        LocationCluster.__init__(self, spawnpoint)
        self.min_time = spawnpoint['time']
        self.max_time = spawnpoint['time']
        self.spawnpoint_id = spawnpoint['spawnpoint_id']
        self.appears = spawnpoint['appears']
        self.leaves = spawnpoint['leaves']

    def append(self, spawnpoint):
        super(self).append(spawnpoint)

        if spawnpoint['time'] < self.min_time:
            self.min_time = spawnpoint['time']

        elif spawnpoint['time'] > self.max_time:
            self.max_time = spawnpoint['time']
            self.spawnpoint_id = spawnpoint['spawnpoint_id']
            self.appears = spawnpoint['appears']
            self.leaves = spawnpoint['leaves']

    def get_score(self, location, time_threshold=-1):
        min_time = min(self.min_time, location['time'])
        max_time = max(self.max_time, location['time'])

        if max_time - min_time > time_threshold:
            return float('inf')
        else:
            return super(self).get_score(self, location)


def cluster_locations(locations, radius=70):
    # Initialize cluster list with the first spawn point available.
    clusters = [LocationCluster(locations.pop())]
    for l in locations:
        # Pick the closest cluster compatible to current spawn point.
        c = min(clusters, key=lambda x: x.get_score(l, -1))

        if c.test_location(l, radius, -1):
            c.append(l)
        else:
            c = LocationCluster(l)
            clusters.append(c)

    return clusters


# Group spawn points with similar spawn times that are close to each other.
def cluster_spawnpoints(spawnpoints, radius=70, time_threshold=240):
    # Initialize cluster list with the first spawn point available.
    clusters = [SpawnCluster(spawnpoints.pop())]
    for sp in spawnpoints:
        # Pick the closest cluster compatible to current spawn point.
        c = min(clusters, key=lambda x: x.get_score(sp, time_threshold))

        if c.test_location(sp, radius, time_threshold):
            c.append(sp)
        else:
            c = SpawnCluster(sp)
            clusters.append(c)

    # Output new spawn points from generated clusters. Use the latest time
    # to be sure that every spawn point in the cluster has already spawned.
    result = []
    for c in clusters:
        result.append({
            'spawnpoint_id': c.spawnpoint_id,
            'lat': c.centroid[0],
            'lng': c.centroid[1],
            'time': c.max_time,
            'appears': c.appears,
            'leaves': c.leaves
        })

    return result
