# Spawnpoint Optimizer

MySQL-only scan optimizer that uses 40x40 slice heatmaps surrounding each spawnpoint to determine how to cover all spawnpoints within step radius of center with as few scans as possible.

Will potentially cause teleporting unless someone wants to solve the traveling salesman problem for the dataset that this generates.

Pass the output CSV to runserver.py using the --csv flag to switch to optimized spawnpoint instead of spiral

![optimized](http://i.imgur.com/Gc0y2zL.png)

## Dependencies

Requires numpy to be installed in addition to upstream requirements

Needs the following function created in MySQL as well:

```sql
create function haversine(lat1 double, lng1 double, lat2 double, lng2 double) returns double deterministic return 12756274 * asin(sqrt(0.5 - cos((lat2 - lat1) * 0.017453292519943295) / 2 + cos(lat1 * 0.017453292519943295) * cos(lat2 * 0.017453292519943295) * (1 - cos((lng2 - lng1) * 0.017453292519943295)) / 2));
```

## Example

    $ python spawncover.py -lat 17.6272249 -lng 138.0100306 -st 5 -sl 100
    Generating spawnpoint data for 17.6272,138.01 (700m radius using 100 heatmap slices)
    Spawnpoints to optimize: 204
    Evaluating unconnected points
    [==============================] Heatmap generation complete
    Full coverage required 56 scan locations
    Cleaning up database
    Coverage approximation via heatmap took 381.390 seconds
    $

