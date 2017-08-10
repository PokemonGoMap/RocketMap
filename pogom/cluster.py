from .utils import equi_rect_distance
from .transform import intermediate_point


class SpawnCluster(object):
    def __init__(self, spawnpoint):
        self._spawnpoints = [spawnpoint]
        self.centroid = (spawnpoint['lat'], spawnpoint['lng'])
        self.min_time = spawnpoint['time']
        self.max_time = spawnpoint['time']
        self.spawnpoint_id = spawnpoint['spawnpoint_id']
        self.appears = spawnpoint['appears']
        self.leaves = spawnpoint['leaves']

    def __getitem__(self, key):
        return self._spawnpoints[key]

    def __iter__(self):
        for x in self._spawnpoints:
            yield x

    def __contains__(self, item):
        return item in self._spawnpoints

    def __len__(self):
        return len(self._spawnpoints)

    def append(self, spawnpoint):
        # Update cluster centroid.
        self.centroid = self.new_centroid(spawnpoint)

        self._spawnpoints.append(spawnpoint)

        if spawnpoint['time'] < self.min_time:
            self.min_time = spawnpoint['time']

        elif spawnpoint['time'] > self.max_time:
            self.max_time = spawnpoint['time']
            self.spawnpoint_id = spawnpoint['spawnpoint_id']
            self.appears = spawnpoint['appears']
            self.leaves = spawnpoint['leaves']

    def new_centroid(self, spawnpoint):
        f = len(self._spawnpoints) / (len(self._spawnpoints) + 1.0)
        new_centroid = intermediate_point(
            (spawnpoint['lat'], spawnpoint['lng']), self.centroid, f)

        return new_centroid


def cost(spawnpoint, cluster, time_threshold):
    sp_position = (spawnpoint['lat'], spawnpoint['lng'])
    distance = equi_rect_distance(sp_position, cluster.centroid) * 1000

    min_time = min(cluster.min_time, spawnpoint['time'])
    max_time = max(cluster.max_time, spawnpoint['time'])

    if max_time - min_time > time_threshold:
        return float('inf')

    return distance


def check_cluster(spawnpoint, cluster, radius, time_threshold):
    # Discard spawn points with infinite cost or too far away.
    if cost(spawnpoint, cluster, time_threshold) > 2 * radius:
        return False

    new_centroid = cluster.new_centroid(spawnpoint)

    # Check if new centroid is close enough to spawn point.
    if equi_rect_distance((spawnpoint['lat'], spawnpoint['lng']),
                          new_centroid) * 1000 > radius:
        return False

    # Check if new centroid is close enough to each spawn points in cluster.
    if any(equi_rect_distance((x['lat'], x['lng']), new_centroid) * 1000 >
            radius for x in cluster):
        return False

    return True


def cluster(spawnpoints, radius, time_threshold):
    clusters = []

    for p in spawnpoints:
        if len(clusters) == 0:
            clusters.append(SpawnCluster(p))
        else:
            c = min(clusters, key=lambda x: cost(p, x, time_threshold))

            if check_cluster(p, c, radius, time_threshold):
                c.append(p)
            else:
                c = SpawnCluster(p)
                clusters.append(c)
    return clusters


def test(cluster, radius, time_threshold):
    assert cluster.max_time - cluster.min_time <= time_threshold

    for p in cluster:
        assert equi_rect_distance((p['lat'], p['lng']),
                                  cluster.centroid) * 1000 <= radius
        assert cluster.min_time <= p['time'] <= cluster.max_time


def cluster_spawnpoints(spawns, radius=70, time_threshold=240):
    # Group spawn points with similar spawn times that are close to each other.
    clusters = cluster(spawns, radius, time_threshold)

    try:
        for c in clusters:
            test(c, radius, time_threshold)
    except AssertionError:
        raise
    # Output spawn points from generated clusters.
    result = []
    for c in clusters:
        sp = dict()
        sp['lat'] = c.centroid[0]
        sp['lng'] = c.centroid[1]
        # Pick the latest time so earlier spawn points have already spawned.
        sp['time'] = c.max_time
        sp['spawnpoint_id'] = c.spawnpoint_id
        sp['appears'] = c.appears
        sp['leaves'] = c.leaves
        result.append(sp)

    return result
