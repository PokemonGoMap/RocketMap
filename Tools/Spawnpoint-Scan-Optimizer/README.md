# Spawnpoint Optimizer

MySQL-only scan optimizer that uses 40x40 slice heatmaps surrounding each spawnpoint to determine how to cover all spawnpoints within step radius of center with as few scans as possible.

Will potentially cause teleporting unless someone wants to solve the traveling salesman problem for the dataset that this generates.

Pass the output CSV to runserver.py using the --csv flag to switch to optimized spawnpoint instead of spiral

![optimized](http://i.imgur.com/Gc0y2zL.png)

## Dependencies

Requires numpy to be installed in addition to upstream requirements

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

