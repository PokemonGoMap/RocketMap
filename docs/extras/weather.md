## Weather overlay on map
The world map is divided by a grid of cells of size 10
([Google s2 library](http://blog.christianperone.com/2015/08/googles-s2-geometry-on-the-sphere-cells-and-hilbert-curve/)).
Each cell has its own weather.
Grid can be rendered by enabling s2cell option in side bar, no scan required for this option.

Weather option adds icons of current weather in cells.
Weather info can be gathered by workers travelling bellow pokemon catch speed limit.

When the screen covers more than half of the cell, weather info on this cell displayed on top bar.

If the weather reaches extreme conditions,
the corresponding cell will change color and an exclamation icon will appear.
