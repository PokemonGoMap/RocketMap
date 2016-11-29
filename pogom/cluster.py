import random

import clsmath


class Spawnpoint(object):
    def __init__(self, data):
        # not needed but useful for debugging
        self.spawnpoint_id = data.get('spawnpoint_id') or data.get('sid')

        self.position = (float(data['lat']), float(data['lng']))

        self.time = data['time']

    def serialize(self):
        obj = dict()

        if self.spawnpoint_id is not None:
            obj['spawnpoint_id'] = self.spawnpoint_id
        obj['lat'] = self.position[0]
        obj['lng'] = self.position[1]
        obj['time'] = self.time

        return obj


class Spawncluster(object):
    def __init__(self, spawnpoint):
        self._spawnpoints = [spawnpoint]
        self.centroid = spawnpoint.position
        self.min_time = spawnpoint.time
        self.max_time = spawnpoint.time

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
        f = len(self._spawnpoints) / (len(self._spawnpoints) + 1.0)
        self.centroid = clsmath.intermediate_point(spawnpoint.position, self.centroid, f)

        self._spawnpoints.append(spawnpoint)

        if spawnpoint.time < self.min_time:
            self.min_time = spawnpoint.time

        if spawnpoint.time > self.max_time:
            self.max_time = spawnpoint.time

    def simulate_centroid(self, spawnpoint):
        f = len(self._spawnpoints) / (len(self._spawnpoints) + 1.0)
        new_centroid = clsmath.intermediate_point(spawnpoint.position, self.centroid, f)

        return new_centroid


def cost(spawnpoint, cluster, time_threshold):
    distance = clsmath.distance(spawnpoint.position, cluster.centroid)

    min_time = min(cluster.min_time, spawnpoint.time)
    max_time = max(cluster.max_time, spawnpoint.time)

    if max_time - min_time > time_threshold:
        return float('inf')

    return distance


def check_cluster(spawnpoint, cluster, radius, time_threshold):
    # discard infinite cost or too far away
    if cost(spawnpoint, cluster, time_threshold) > 2 * radius:
        return False

    new_centroid = cluster.simulate_centroid(spawnpoint)

    # we'd be removing ourselves
    if clsmath.distance(spawnpoint.position, new_centroid) > radius:
        return False

    # we'd be removing x
    if any(clsmath.distance(x.position, new_centroid) > radius for x in cluster):
        return False

    return True


def cluster(spawnpoints, radius, time_threshold):
    clusters = []

    for p in spawnpoints:
        if len(clusters) == 0:
            clusters.append(Spawncluster(p))
        else:
            c = min(clusters, key=lambda x: cost(p, x, time_threshold))

            if check_cluster(p, c, radius, time_threshold):
                c.append(p)
            else:
                c = Spawncluster(p)
                clusters.append(c)
    return clusters


def test(cluster, radius, time_threshold):
    assert cluster.max_time - cluster.min_time <= time_threshold

    for p in cluster:
        assert clsmath.distance(p.position, cluster.centroid) <= radius
        assert cluster.min_time <= p.time <= cluster.max_time


def main(raw):
    radius = 70
    time_threshold = 180  # 4 minutes is alright to grab a pokemon since most times are 30m+
    spawnpoints = [Spawnpoint(x) for x in raw]  # separate them
    clusters = cluster(spawnpoints, radius, time_threshold)

    try:
        for c in clusters:
            test(c, radius, time_threshold)
    except AssertionError:
        print 'error: something\'s seriously broken.'
        raise

    clusters.sort(key=lambda x: len(x))

    rows = []  # Clear rows to prevent multiplying spawn points.
    for c in clusters:
        row = dict()
        # pick a random id from a clustered spawnpoint
        # we should probably not do this
        row['spawnpoint_id'] = random.choice(c).spawnpoint_id
        row['lat'] = c.centroid[0]
        row['lng'] = c.centroid[1]
        # pick the latest time so earlier spawnpoints have already spawned
        row['time'] = c.max_time
        rows.append(row)

    return rows
