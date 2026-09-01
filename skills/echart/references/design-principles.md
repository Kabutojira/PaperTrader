# Data Visualization Design Principles

## Table of Contents
- Fundamental Rules (axis baselines, data-ink ratio)
- Chart Type Selection (when to use each chart)
- Color Principles (colorblind-safe palettes, sequential vs diverging)
- Typography & Labels (titles, label formatting, axis formatting)
- Hierarchy & Layout (visual hierarchy, progressive disclosure)
- Consistency (uniformity guidelines)
- Accessibility Checklist
- Context & Credibility (data source, error communication)
- When NOT to Use a Chart

## Fundamental Rules (Non-Negotiable)

### Axis Baselines
- **Bar/Column charts**: Value axis MUST start at zero. Heights represent proportional values.
- **Line charts**: Do NOT require zero baseline. Position and angle convey meaning, not bar height.
- **Pie charts**: Must represent exactly 100% of data. All slices must sum to 100%.

### Data-Ink Ratio
Remove all "chart junk":
- No 3D effects (unless data is actually 3-dimensional)
- No shadows or decorative elements
- No thick borders or unnecessary gridlines
- Justify every visual element - if it doesn't aid understanding, remove it

## Chart Type Selection

### When to Use Each Chart

| Chart Type | Best For | Avoid When |
|------------|----------|------------|
| Bar/Column | Comparing categories | >15 categories |
| Line | Trends over time | Non-continuous data |
| Pie/Donut | Part-to-whole (≤5 slices) | Comparing similar values |
| Scatter | Correlation between variables | Categorical data |
| Heatmap | Patterns in matrix data | Few data points |
| Stacked Bar | Composition + comparison | Many categories |

### Pie Chart Rules
- Maximum 5 slices (use bar chart for more)
- Arrange largest to smallest, clockwise from 12 o'clock
- Consider donut chart for cleaner center labeling

### Bar Chart Guidance
- Use horizontal bars for long labels (don't rotate text)
- Order logically: by value, alphabetically, or sequentially for time

## Color Principles

### Colorblind-Safe Palettes

**Paul Tol Bright** (recommended default):
```javascript
['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB']
// Blue, Red, Green, Yellow, Cyan, Purple, Grey
```

**Paul Tol Vibrant**:
```javascript
['#EE7733', '#0077BB', '#33BBEE', '#EE3377', '#CC3311', '#009988', '#BBBBBB']
// Orange, Blue, Cyan, Magenta, Red, Teal, Grey
```

**Paul Tol Muted**:
```javascript
['#CC6677', '#332288', '#DDCC77', '#117733', '#88CCEE', '#882255', '#44AA99', '#999933', '#AA4499']
// Rose, Indigo, Sand, Green, Cyan, Wine, Teal, Olive, Purple
```

**High Contrast** (works in grayscale):
```javascript
['#004488', '#DDAA33', '#BB5566']
// Blue, Yellow, Red
```

**Categorical (8 colors)**:
```javascript
['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
```

### Color Selection Rules

1. **Avoid red-green combinations** - most common colorblindness
2. **Blue is safest** - least affected by color vision deficiencies
3. **Use "earthier" versions** - olive over bright green, navy over neon blue
4. **Test in grayscale** - ensure distinguishability without color
5. **Match meaning to culture** - avoid red for positive metrics, green for negative
6. **Limit to 7 colors** - human perception limit for distinct categories

### Sequential vs Diverging

**Sequential** (one direction): Use for data from low to high
```javascript
// Blues
['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#084594']
```

**Diverging** (two directions from center): Use for data with meaningful midpoint
```javascript
// Red-Blue
['#b2182b', '#ef8a62', '#fddbc7', '#f7f7f7', '#d1e5f0', '#67a9cf', '#2166ac']
```

## Typography & Labels

### Title Guidelines
- Write active, narrative titles that tell the story
- Combine narrative title with technical subtitle if needed
- Example: "Sales Doubled in Q4" (title) + "Quarterly Revenue 2024" (subtitle)

### Label Best Practices
- Use commas as thousands separators: `1,000,000` not `1000000`
- Keep labels horizontal - convert to horizontal bar chart if labels are long
- Use bold sparingly - only for key insights
- Direct labeling on chart elements can replace legends

### Axis Formatting
- Use natural, equal increments: 0, 20, 40, 60, 80, 100
- Include units in axis title or labels
- Don't overload with excessive tick marks

## Hierarchy & Layout

### Visual Hierarchy Techniques
1. **Size** - Larger elements draw attention first
2. **Color saturation** - Brighter colors for important data, grey for context
3. **Position** - Top-left is read first in western cultures
4. **Contrast** - High contrast elements stand out

### Progressive Disclosure
- Show summary first, details on interaction
- Use tooltips for supplementary info (not essential data)
- Filter/drill-down for complex datasets

## Consistency

### Maintain Uniformity In:
- Color assignments across related charts
- Typography hierarchy
- Interaction patterns (hover, click, selection)
- Spacing and alignment
- Number formatting

## Accessibility Checklist

1. [ ] Color palette tested with colorblind simulator
2. [ ] Works in grayscale for print
3. [ ] Text meets contrast requirements (4.5:1 minimum)
4. [ ] Essential info not conveyed by color alone
5. [ ] Patterns/textures as backup to color coding
6. [ ] Alt text/descriptions for screen readers
7. [ ] Keyboard navigable interactions

## Context & Credibility

### Always Include
- **Data source** - Where the data came from
- **Time period** - When data was collected
- **Units** - What's being measured
- **Sample size** - If applicable

### Error Communication
- Show error bars when uncertainty exists
- Include margin of error in annotations
- Be honest about data limitations

## When NOT to Use a Chart

Sometimes alternatives communicate better:
- **Single number**: Use a big number display, not a chart
- **Two numbers**: Simple text comparison may suffice
- **Precise values needed**: Use a table
- **No meaningful pattern**: Don't force visualization

Ask: "Does visualizing this data pattern actually matter to the story?"
