from __future__ import division
from __future__ import absolute_import
from past.utils import old_div

from . import clsmath


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
        # update centroid
        f = old_div(len(self._spawnpoints), (len(self._spawnpoints) + 1.0))
        self.centroid = clsmath.intermediate_point(
            (spawnpoint['lat'], spawnpoint['lng']), self.centroid, f)

        self._spawnpoints.append(spawnpoint)

        if spawnpoint['time'] < self.min_time:
            self.min_time = spawnpoint['time']

        elif spawnpoint['time'] > self.max_time:
            self.max_time = spawnpoint['time']
            self.spawnpoint_id = spawnpoint['spawnpoint_id']
            self.appears = spawnpoint['appears']
            self.leaves = spawnpoint['leaves']

    def simulate_centroid(self, spawnpoint):
        f = old_div(len(self._spawnpoints), (len(self._spawnpoints) + 1.0))
        new_centroid = clsmath.intermediate_point(
            (spawnpoint['lat'], spawnpoint['lng']), self.centroid, f)

        return new_centroid


def cost(spawnpoint, cluster, time_threshold):
    sp_position = (spawnpoint['lat'], spawnpoint['lng'])
    distance = clsmath.distance(sp_position, cluster.centroid)

    min_time = min(cluster.min_time, spawnpoint['time'])
    max_time = max(cluster.max_time, spawnpoint['time'])

    if max_time - min_time > time_threshold:
        return float('inf')

    return distance


def check_cluster(spawnpoint, cluster, radius, time_threshold):
    # discard infinite cost or too far away
    if cost(spawnpoint, cluster, time_threshold) > 2 * radius:
        return False

    new_centroid = cluster.simulate_centroid(spawnpoint)

    # we'd be removing ourselves
    if clsmath.distance((spawnpoint['lat'], spawnpoint['lng']),
                        new_centroid) > radius:
        return False

    # we'd be removing x
    if any(clsmath.distance((x['lat'], x['lng']), new_centroid) > radius
            for x in cluster):
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
        assert clsmath.distance((p['lat'], p['lng']),
                                cluster.centroid) <= radius
        assert cluster.min_time <= p['time'] <= cluster.max_time


def cluster_spawnpoints(spawns, radius=70, time_threshold=240):
    # 4 minutes is alright to grab a pokemon since most times are 30m+
    clusters = cluster(spawns, radius, time_threshold)

    try:
        for c in clusters:
            test(c, radius, time_threshold)
    except AssertionError:
        raise

    clusters.sort(key=lambda x: len(x))

    result = []  # Clear rows to prevent multiplying spawn points.
    for c in clusters:
        sp = dict()
        sp['lat'] = c.centroid[0]
        sp['lng'] = c.centroid[1]
        # pick the latest time so earlier spawnpoints have already spawned
        sp['time'] = c.max_time
        sp['spawnpoint_id'] = c.spawnpoint_id
        sp['appears'] = c.appears
        sp['leaves'] = c.leaves
        result.append(sp)

    return result
