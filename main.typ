#table(
    stroke: none,
    columns: (1fr,) * 6,
    align: (horizon, horizon, left, right, right, right),

    table.hline(stroke: 2pt),
    table.header(
      repeat: true,
      [*Size*], [*Maze*], [*Algorithm*], [*Path Len*], [*Explored*], [*Time (ms)*],
      table.hline(),
    ),

    
    table.cell(rowspan: 18)[$128 times 128$ ],
    table.cell(rowspan: 6)[Random Density],
    [DFS], [879.3], [4448.5], [512.95],
    [BFS], [255.0], [13074.5], [226.21],
    [Dijkstra], [255.0], [13074.6], [271.44],
    [A\*], [255.0], [8113.3], [248.30],
    [A\* Plus], [255.0], [907.3], [11.17],
    [JPS (4-Way)], [255.0], [7875.0], [245.41],
    table.hline(stroke: .5pt),

    table.cell(rowspan: 6)[Braid Maze],
    [DFS], [1460.9], [3853.1], [45.52],
    [BFS], [524.7], [8330.2], [92.57],
    [Dijkstra], [524.7], [8333.8], [105.79],
    [A\*], [524.7], [6846.1], [81.48],
    [A\* Plus], [524.7], [6615.2], [77.81],
    [JPS (4-Way)], [524.7], [6054.9], [38.87],
    table.hline(stroke: .5pt),

    table.cell(rowspan: 6)[Perfect Maze],
    [DFS], [2365.9], [2902.2], [22.52],
    [BFS], [2365.9], [4931.6], [49.80],
    [Dijkstra], [2365.9], [4931.7], [52.38],
    [A\*], [2365.9], [4699.5], [50.01],
    [A\* Plus], [2365.9], [4682.5], [50.28],
    [JPS (4-Way)], [2365.9], [4164.0], [50.14],
    table.hline(stroke: .5pt),

    table.hline(stroke: 2pt),
  )

#table(
    stroke: none,
    columns: (1fr,) * 6,
    align: (horizon, horizon, left, right, right, right),

    table.hline(stroke: 2pt),
    table.header(
      repeat: true,
      [*Size*], [*Maze*], [*Algorithm*], [*Path Len*], [*Explored*], [*Time (ms)*],
      table.hline(),
    ),

    
    table.cell(rowspan: 18)[$128 times 128$ ],

    table.cell(rowspan: 6)[Cave Maze],
    [DFS], [1964.8], [5324.1], [416.34],
    [BFS], [256.3], [10860.6], [154.41],
    [Dijkstra], [256.3], [10861.6], [187.43],
    [A\*], [256.3], [5120.1], [106.13],
    [A\* Plus], [256.4], [1954.3], [24.80],
    [JPS (4-Way)], [256.3], [5115.3], [122.33],
    table.hline(stroke: .5pt),

    table.cell(rowspan: 6)[Prim Maze],
    [DFS], [295.0], [3444.7], [24.68],
    [BFS], [295.0], [7153.9], [72.08],
    [Dijkstra], [295.0], [7162.3], [87.75],
    [A\*], [295.0], [2484.1], [21.40],
    [A\* Plus], [295.0], [2087.9], [16.54],
    [JPS (4-Way)], [295.0], [1576.6], [7.06],
    table.hline(stroke: .5pt),

    table.cell(rowspan: 6)[Recursive Division],
    [DFS], [630.0], [3654.2], [30.22],
    [BFS], [630.0], [6663.8], [63.08],
    [Dijkstra], [630.0], [6667.8], [71.64],
    [A\*], [630.0], [5549.8], [55.75],
    [A\* Plus], [630.0], [5461.9], [55.01],
    [JPS (4-Way)], [630.0], [3662.7], [22.44],

    table.hline(stroke: 2pt),
  )