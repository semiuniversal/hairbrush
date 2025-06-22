# H.Airbrush G-code Generator

## Z-Movement Optimization

The Z-axis on the H.Airbrush plotter moves approximately 20x slower than the X and Y axes. This has significant implications for print time and efficiency. We've implemented several optimizations to minimize Z movements:

### 1. Path Batching

Paths with the same brush and Z-height are grouped together to minimize tool changes and Z movements:

- Paths are queued rather than immediately processed
- Paths are grouped by brush type and Z-height
- Z is raised only once per batch
- Air is turned on once per batch
- Z is lowered once per path in the batch
- Only paint flow is toggled between paths in the same batch

### 2. Test Pattern Optimization

The test pattern grid is drawn with minimal Z movements:

- Z is lowered once at the beginning
- All horizontal lines are drawn without raising Z
- All vertical lines are drawn without raising Z
- All diagonal lines are drawn without raising Z
- Z is raised only once at the end

### 3. Working Plane Alignment

The working plane alignment procedure minimizes Z movements:

- Z is raised once at the beginning
- Z is lowered once to Z=0
- All reference points are defined with XY movements only (Z stays at 0)
- Z is raised once at the end

### 4. Machine Initialization

Machine initialization has been optimized:

- Z is raised once at the beginning
- Z is lowered once to define Z=0
- Z is raised once after defining the origin
- All airbrush systems are initialized in a single batch

## SVG Path Processing

Since SVG specification does not permit a single stroke to have varying width or opacity, we use a consistent Z-height for each path. This works well with our Z-movement optimization strategy, as we can batch paths with the same properties together.

## Implementation Details

The G-code generation follows these principles:

1. Minimize Z movements by batching paths with similar properties
2. Strictly separate Z and XY movements to maintain flat drawings
3. Use proper G17 commands to ensure working in the X-Y plane
4. Optimize travel moves between paths in the same batch

This approach significantly reduces print time while maintaining drawing quality. 