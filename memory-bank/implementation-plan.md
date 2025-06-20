# Implementation Plan

## Overview
This document outlines a staged approach to implementing the dual-airbrush plotter software. Each stage builds on the previous one, with clear deliverables and testing criteria. The plan focuses on incremental development with frequent validation points to ensure the system meets artist requirements.

## Stage 1: Environment Setup and Research
**Goal**: Establish the development environment and conduct necessary research.

**Tasks**:
1. Verify WSL installation and configure Linux environment
2. Install Python 3.x and uv in WSL
3. Create project directory structure
4. Set up version control
5. Create pyproject.toml for dependency management
6. Initialize uv virtual environment
7. Install basic dependencies (PyYAML, etc.)
8. Research Inkscape extension development
9. Research Duet 2 WiFi G-code command structure
10. Document environment setup process

**Deliverables**:
- Functioning WSL development environment
- Project structure with proper directory organization
- Version-controlled repository
- Working Python environment with uv
- Research documentation on Inkscape extensions and Duet G-code
- Basic documentation for setup

**Testing Criteria**:
- Python and uv work correctly in WSL
- Dependencies can be installed via pyproject.toml
- Project structure supports the planned components
- Research provides clear path for extension development

## Stage 2: Core Library Development
**Goal**: Implement the foundational libraries for SVG processing and G-code generation.

**Tasks**:
1. Design the YAML schema for command templates
2. Create a parser for the command templates
3. Implement basic template validation
4. Create sample templates for Duet 2 WiFi board
5. Create utilities for parsing SVG files
6. Implement path extraction from layers
7. Handle basic path transformations
8. Write unit tests for core libraries
9. Document the core library functionality

**Deliverables**:
- Core library package structure
- YAML template parser and validator
- SVG parsing utilities
- Path transformation handlers
- Sample template files
- Unit tests for core functionality
- Documentation for core libraries

**Testing Criteria**:
- Parser correctly loads and validates YAML templates
- SVG parser successfully extracts paths from files
- Path transformations maintain precision and structure
- Unit tests validate core functionality

## Stage 3: G-code Generation Engine
**Goal**: Implement the G-code generation engine that converts SVG paths to machine commands.

**Tasks**:
1. Create a G-code generator class
2. Implement path to G-code conversion
3. Add support for brush control commands
4. Implement brush offset handling
5. Create output formatting and file writing
6. Create functions to convert SVG paths to plotter movements
7. Write unit tests for G-code generation
8. Document the G-code generation process

**Deliverables**:
- G-code generator implementation
- Path to G-code conversion logic
- Brush control integration
- Output file handling
- Unit tests for G-code generation
- Documentation for G-code generation

**Testing Criteria**:
- Correctly converts paths to G-code
- Properly inserts brush control commands
- Handles brush offsets accurately
- Generates valid G-code for Duet 2 WiFi
- Maintains path precision during conversion

## Stage 4: Inkscape Extension Development
**Goal**: Create the Inkscape extension that provides the user interface.

**Tasks**:
1. Create the .inx file for the extension
2. Implement the extension UI with parameter inputs
3. Connect the UI to the G-code generator
4. Handle parameter validation and error reporting
5. Implement file output selection
6. Create a proof-of-concept with simple SVG files
7. Write documentation for the extension
8. Create a basic user guide

**Deliverables**:
- Inkscape extension .inx file
- Extension UI implementation
- Parameter handling and validation
- Integration with G-code generator
- User documentation for the extension
- Installation instructions for the extension

**Testing Criteria**:
- Extension loads correctly in Inkscape
- UI allows configuration of all required parameters
- Parameters are correctly passed to the G-code generator
- Extension produces valid output files
- Error handling provides useful feedback

## Stage 5: Integration and Testing
**Goal**: Integrate all components and perform comprehensive testing with real-world examples.

**Tasks**:
1. Integrate the command template system, SVG processing, and G-code generation
2. Create end-to-end tests with sample SVG files
3. Implement error handling and logging
4. Optimize performance for large SVG files
5. Create sample SVG files for testing
6. Test with complex real-world examples
7. Document the integrated system
8. Create comprehensive installation instructions

**Deliverables**:
- Fully integrated system
- End-to-end tests
- Error handling and logging implementation
- Sample SVG files
- Performance optimization
- Comprehensive documentation
- Installation guide

**Testing Criteria**:
- System successfully processes SVG files end-to-end
- Generates correct G-code for various test cases
- Handles errors gracefully with helpful messages
- Performs efficiently with large SVG files
- Works with complex real-world examples

## Stage 6: Refinement and User Feedback
**Goal**: Refine the system based on user testing and feedback.

**Tasks**:
1. Conduct user testing with artists
2. Collect and analyze feedback
3. Implement high-priority improvements
4. Enhance documentation based on user questions
5. Create additional examples and tutorials
6. Optimize performance bottlenecks
7. Implement usability improvements

**Deliverables**:
- User testing results
- Improved system based on feedback
- Enhanced documentation
- Additional examples and tutorials
- Performance optimizations
- Usability improvements

**Testing Criteria**:
- System addresses key user feedback
- Documentation answers common questions
- Examples demonstrate key use cases
- Performance meets user expectations

## Stage 7: Phase 2 Planning (Optional Components)
**Goal**: Plan the implementation of optional components based on user needs.

**Tasks**:
1. Evaluate requirements for Telnet Controller
2. Assess needs for Calibration & Manual Mode GUI
3. Create detailed specifications for optional components
4. Prioritize optional features based on user feedback
5. Update the implementation plan
6. Create proof-of-concept for highest priority optional component

**Deliverables**:
- Detailed specifications for optional components
- Prioritized feature list based on user needs
- Updated implementation plan
- Proof-of-concept for highest priority component

**Testing Criteria**:
- Specifications align with overall system architecture
- Features are prioritized based on user needs
- Plan provides clear path for implementation
- Proof-of-concept demonstrates feasibility

## Timeline and Dependencies
- **Stage 1** (Environment Setup and Research): 2-3 days
- **Stage 2** (Core Library Development): 3-4 days, depends on Stage 1
- **Stage 3** (G-code Generation Engine): 3-4 days, depends on Stage 2
- **Stage 4** (Inkscape Extension Development): 3-4 days, depends on Stage 1 research
- **Stage 5** (Integration and Testing): 4-5 days, depends on Stages 3 and 4
- **Stage 6** (Refinement and User Feedback): 3-5 days, depends on Stage 5
- **Stage 7** (Phase 2 Planning): 2-3 days, depends on Stage 6

## Risk Management
- **Inkscape Extension API Complexity**: Research early in Stage 1, create simple proof-of-concept in Stage 4
- **SVG Path Transformation Challenges**: Test with various SVG complexity levels in Stage 2
- **G-code Compatibility**: Verify with Duet documentation in Stage 1, create validation tests in Stage 3
- **WSL/Windows Integration**: Test file access and permissions early in Stage 1
- **User Experience Gaps**: Address through user testing in Stage 6
- **Performance with Complex SVGs**: Test with increasingly complex files throughout development

## Current Implementation Plan (High Priority Tasks)

### Task 1: Improve Curve Handling in Path Processing

**Goal**: Enhance the accuracy of curve approximation, especially for Bezier curves and arcs.

**Approach**:
1. Enhance the `path_to_polyline` method in `PathProcessor` class:
   - Implement adaptive segmentation for curves based on curvature
   - Add proper support for all SVG path commands (S, Q, T, A)
   - Fix the coordinate system transformation issues

**Specific Changes**:
1. Update `path_to_polyline` method:
   - Add curvature-based adaptive segmentation for Bezier curves
   - Implement proper handling for smooth cubic (S) and quadratic (Q, T) curves
   - Add proper arc (A) command handling with elliptical arc approximation
2. Add helper methods:
   - `_adaptive_bezier_segmentation` to calculate appropriate number of segments based on curve complexity
   - `_calculate_smooth_control_point` for handling smooth curve continuity
   - `_approximate_arc` for converting arcs to line segments

**Deliverables**:
- Enhanced path_processor.py with improved curve handling
- Test cases demonstrating curve accuracy improvements
- Documentation of the curve approximation algorithms

### Task 2: Fix Path Distortion Issues in G-code Output

**Goal**: Ensure accurate translation of SVG paths to G-code coordinates.

**Approach**:
1. Implement proper scaling and transformation between SVG and G-code coordinate systems
2. Add debugging markers to visualize path conversion
3. Ensure path orientation and direction are preserved

**Specific Changes**:
1. Update `GCodeGenerator.add_path` method:
   - Add SVG viewBox handling to ensure proper scaling
   - Implement SVG transform attribute handling
   - Add optional debug markers at key points
2. Add coordinate system transformation utilities:
   - Create `transform_coordinates` method to handle SVG to machine space conversion
   - Add support for SVG transformations (scale, rotate, translate)

**Deliverables**:
- Enhanced gcode_generator.py with proper coordinate transformation
- Debug visualization option for path conversion
- Documentation of the coordinate system handling

### Task 3: Enhance SVG to G-code Conversion Process

**Goal**: Improve the overall conversion process with better configuration options and error handling.

**Approach**:
1. Add more configuration options for curve resolution
2. Implement better error handling for invalid paths
3. Add progress reporting for long conversions

**Specific Changes**:
1. Update `convert_svg_to_gcode` function in path_to_gcode.py:
   - Add curve_resolution parameter with adaptive defaults
   - Add validation for path data before processing
   - Implement progress reporting for large files
2. Enhance error handling:
   - Add specific exception types for different error cases
   - Provide more detailed error messages
   - Add recovery options for some error conditions

**Deliverables**:
- Enhanced path_to_gcode.py with improved configuration options
- Better error messages and handling
- Progress reporting for long-running conversions

### Task 4: Test with Complex SVG Files

**Goal**: Validate the improvements with a variety of test cases.

**Approach**:
1. Create test SVG files with different curve types
2. Validate G-code output with visualization tools
3. Compare output with reference implementations

**Specific Changes**:
1. Create test directory with sample SVG files:
   - Simple shapes (circles, ellipses, rectangles)
   - Complex curves (Bezier curves, arcs)
   - Combined paths with different command types
2. Implement visualization tools:
   - Add G-code preview functionality
   - Create SVG to G-code comparison visualization

**Deliverables**:
- Test suite with various SVG complexity levels
- Visualization tools for G-code validation
- Documentation of test results and comparisons

## Implementation Timeline

1. **Week 1: Curve Handling Improvements**
   - Day 1-2: Implement adaptive segmentation for Bezier curves
   - Day 3-4: Add support for smooth curves and arcs
   - Day 5: Create test cases and validate improvements

2. **Week 2: Coordinate Transformation and Path Distortion Fixes**
   - Day 1-2: Implement proper scaling and transformation
   - Day 3: Add debugging visualization
   - Day 4-5: Test and refine coordinate handling

3. **Week 3: Enhanced Configuration and Testing**
   - Day 1-2: Add configuration options and error handling
   - Day 3-4: Create comprehensive test suite
   - Day 5: Document improvements and update user guides

## Success Criteria
- Bezier curves and arcs are accurately approximated with minimal distortion
- SVG paths are correctly scaled and positioned in G-code output
- Error handling provides useful feedback for invalid paths
- Configuration options allow fine-tuning of the conversion process
- Test suite validates improvements across different SVG complexity levels

## Implementation Progress Summary

### Completed Tasks

1. **Improved Curve Handling in Path Processing**
   - Added adaptive segmentation for Bezier curves based on curvature
   - Implemented proper support for all SVG path commands (C, S, Q, T, A)
   - Added helper methods for calculating control points and approximating arcs
   - Improved curve resolution with curvature-based segmentation

2. **Enhanced G-code Generation**
   - Added SVG viewBox and document dimensions handling
   - Implemented coordinate transformation between SVG and G-code space
   - Added debug markers for visualizing path conversion
   - Improved error handling and progress reporting

3. **Created Testing Framework**
   - Created test SVG file with various curve types
   - Implemented test scripts for path processing and G-code generation
   - Added visualization tools for G-code output

### Remaining Tasks

1. **Coordinate System Transformation**
   - Further improve coordinate system transformation to handle all SVG transformations
   - Ensure path orientation and direction are preserved

2. **Testing with Complex SVG Files**
   - Create more complex test cases with different curve types
   - Validate G-code output with visualization tools
   - Compare output with reference implementations

3. **Research Duet 2 WiFi G-code**
   - Research Duet 2 WiFi G-code command structure
   - Create specific G-code templates for the Duet 2 WiFi board

4. **Integration with Inkscape Extension**
   - Update the Inkscape extension to use the improved path processing
   - Add new configuration options to the extension UI

### Next Immediate Steps

1. Create additional test SVG files with more complex paths and transformations
2. Research Duet 2 WiFi G-code command structure
3. Update the Inkscape extension to use the improved path processing
4. Test the extension with the new path processing improvements

## SVG to G-code Conversion Improvement Plan

After analyzing the AxiDraw extension code and identifying the key differences with our current implementation, this plan outlines specific improvements needed to enhance the SVG to G-code conversion process for the dual-airbrush plotter.

### 1. SVG Parsing Enhancements

**Goal**: Improve SVG parsing to handle all SVG elements and namespaces correctly, similar to AxiDraw's approach.

**Implementation Steps**:

1. **Enhance Namespace Handling**:
   - Update the SVG parser to handle Inkscape-specific namespaces properly
   - Implement fallback mechanisms for undefined namespaces
   - Add support for different namespace conventions in SVG files

2. **Improve Document Properties Extraction**:
   - Extract and properly interpret viewBox, width, height attributes
   - Handle unit conversions (mm, px, in, etc.) correctly
   - Parse document-level transformations

3. **Enhance Layer and Group Handling**:
   - Implement proper layer detection with Inkscape namespace support
   - Add support for nested groups and their transformations
   - Preserve layer hierarchy for organized G-code output

**Deliverables**:
- Enhanced SVG parser with robust namespace handling
- Improved document properties extraction
- Layer and group hierarchy preservation

### 2. Path Processing Improvements

**Goal**: Implement sophisticated path processing that accurately handles all SVG path commands and transformations.

**Implementation Steps**:

1. **Complete SVG Path Command Support**:
   - Implement proper handling for all SVG path commands (M, L, H, V, C, S, Q, T, A, Z)
   - Add support for relative and absolute coordinates for each command
   - Implement path closing (Z command) with proper handling

2. **Enhance Curve Approximation**:
   - Implement adaptive segmentation for Bezier curves based on curvature
   - Add proper approximation for elliptical arcs (A command)
   - Implement smooth curve continuity for S and T commands
   - Add configurable curve resolution with intelligent defaults

3. **Implement Transformation Support**:
   - Add support for SVG transformation matrices
   - Handle nested transformations correctly
   - Implement proper scaling, rotation, translation, and skewing

**Deliverables**:
- Complete path command processor with support for all SVG commands
- Adaptive curve approximation algorithms
- Transformation handling system

### 3. Coordinate System Transformation

**Goal**: Ensure accurate transformation from SVG coordinate space to machine coordinate space.

**Implementation Steps**:

1. **SVG Coordinate System Handling**:
   - Implement proper interpretation of SVG coordinate system (origin at top-left)
   - Handle viewBox transformations correctly
   - Support different unit systems and conversions

2. **Machine Coordinate System Mapping**:
   - Implement mapping from SVG space to machine space
   - Add configurable scaling and offset parameters
   - Support for mirroring and orientation changes

3. **Boundary and Clipping Support**:
   - Add support for clipping paths to machine boundaries
   - Implement warnings for paths outside plottable area
   - Add scaling options to fit designs to available space

**Deliverables**:
- Coordinate transformation system
- Unit conversion utilities
- Boundary handling and clipping functions

### 4. G-code Generation Improvements

**Goal**: Generate optimized G-code that correctly represents SVG paths and supports dual-airbrush control.

**Implementation Steps**:

1. **G-code Command Optimization**:
   - Research and implement optimal G-code commands for Duet 2 WiFi
   - Add proper formatting and comments in G-code output
   - Implement machine initialization and finalization sequences

2. **Dual-Airbrush Control**:
   - Implement channel separation based on fill/stroke colors
   - Add support for varying opacity levels to control airbrush pressure
   - Implement proper tool changes between black and white channels

3. **Path Optimization**:
   - Implement path sorting to minimize travel moves
   - Add path simplification options for complex SVGs
   - Implement travel move optimization

**Deliverables**:
- Optimized G-code generator
- Dual-airbrush control commands
- Path optimization algorithms

### 5. Testing and Validation

**Goal**: Create comprehensive testing tools to validate the SVG to G-code conversion process.

**Implementation Steps**:

1. **Test SVG Creation**:
   - Create test SVGs with various path types (lines, curves, arcs)
   - Include complex real-world examples
   - Create SVGs that test specific edge cases

2. **Visualization Tools**:
   - Implement G-code visualization for preview
   - Add debug visualization options to show path approximations
   - Create comparison tools to validate output against reference implementations

3. **Validation Framework**:
   - Create automated tests for SVG parsing and G-code generation
   - Implement validation checks for G-code correctness
   - Add performance benchmarks for large SVG files

**Deliverables**:
- Test SVG suite
- G-code visualization tools
- Automated testing framework

### 6. Documentation and User Guide

**Goal**: Create comprehensive documentation for developers and users.

**Implementation Steps**:

1. **Developer Documentation**:
   - Document SVG parsing and path processing algorithms
   - Create API documentation for core libraries
   - Add code examples for extension points

2. **User Guide**:
   - Create installation and setup instructions
   - Add usage guide with examples
   - Document configuration options and best practices

3. **Troubleshooting Guide**:
   - Create common issues and solutions section
   - Add debugging tips
   - Include performance optimization suggestions

**Deliverables**:
- Developer documentation
- User guide
- Troubleshooting guide

### Implementation Timeline

1. **SVG Parsing Enhancements**: 3-4 days
2. **Path Processing Improvements**: 4-5 days
3. **Coordinate System Transformation**: 2-3 days
4. **G-code Generation Improvements**: 3-4 days
5. **Testing and Validation**: 2-3 days
6. **Documentation and User Guide**: 2-3 days

**Total Estimated Time**: 16-22 days

### Key Dependencies and References

1. **AxiDraw Extension Code**:
   - digest_svg.py for SVG parsing approach
   - path_objects.py for path representation
   - motion.py for trajectory planning concepts

2. **SVG Specification**:
   - SVG 1.1 and 2.0 path commands
   - Coordinate systems and transformations
   - Units and viewBox handling

3. **G-code References**:
   - Duet 2 WiFi G-code documentation
   - RepRap G-code reference
   - Inkscape G-code extension examples

This implementation plan focuses on adapting the proven approaches from AxiDraw's SVG processing while changing the output to generate proper G-code for the dual-airbrush plotter. By leveraging existing knowledge and code structures, we can minimize reinvention and focus on the unique aspects of our system. 