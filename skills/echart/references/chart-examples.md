# ECharts v6 Comprehensive Examples

## Table of Contents
- Line Charts (basic, smooth, area, multiple, stacked, mark points, step, custom style, null data)
- Bar Charts (basic, background, horizontal, grouped, stacked, gradient, rounded, waterfall)
- Pie Charts (basic, donut, half donut, nested, rose/nightingale)
- Scatter Charts (basic, bubble, categories, effect/animation, custom symbol, jittered v6)
- Rich Text Labels (basic, icons/images, background/border, rotated, complex layout)
- Radar Charts (basic, multiple series)
- Heatmap (calendar, cartesian)
- Candlestick / Financial (basic, with volume)
- Gauge (basic, multi-gauge dashboard)
- Funnel
- Sankey
- Treemap
- Sunburst
- Graph / Network
- Boxplot
- Parallel Coordinates
- ECharts v6 New Features (chord, dynamic theme switching, v5 colors)

Reference for Apache ECharts v6.

Download: https://github.com/apache/echarts/releases

```html
<script src="./lib/echarts.min.js"></script>
<div id="chart" style="width: 800px; height: 500px;"></div>
<script>
  const chart = echarts.init(document.getElementById('chart'));
  chart.setOption(option);  // option defined in examples below
</script>
```

## Line Charts

### Basic Line
```javascript
option = {
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{ data: [150, 230, 224, 218, 135, 147, 260], type: 'line' }]
};
```

### Smooth Line
```javascript
option = {
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{ data: [820, 932, 901, 934, 1290, 1330, 1320], type: 'line', smooth: true }]
};
```

### Area Chart
```javascript
option = {
  xAxis: { type: 'category', boundaryGap: false, data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{
    data: [820, 932, 901, 934, 1290, 1330, 1320],
    type: 'line',
    areaStyle: {}
  }]
};
```

### Multiple Lines with Legend
```javascript
option = {
  title: { text: 'Sales Comparison' },
  tooltip: { trigger: 'axis' },
  legend: { data: ['2023', '2024'] },
  xAxis: { type: 'category', boundaryGap: false, data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
  yAxis: { type: 'value' },
  series: [
    { name: '2023', type: 'line', data: [120, 132, 101, 134, 90, 230] },
    { name: '2024', type: 'line', data: [220, 182, 191, 234, 290, 330] }
  ]
};
```

### Stacked Area Chart
```javascript
option = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } } },
  legend: { data: ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine'] },
  xAxis: { type: 'category', boundaryGap: false, data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [
    { name: 'Email', type: 'line', stack: 'Total', areaStyle: {}, emphasis: { focus: 'series' }, data: [120, 132, 101, 134, 90, 230, 210] },
    { name: 'Union Ads', type: 'line', stack: 'Total', areaStyle: {}, emphasis: { focus: 'series' }, data: [220, 182, 191, 234, 290, 330, 310] },
    { name: 'Video Ads', type: 'line', stack: 'Total', areaStyle: {}, emphasis: { focus: 'series' }, data: [150, 232, 201, 154, 190, 330, 410] },
    { name: 'Direct', type: 'line', stack: 'Total', areaStyle: {}, emphasis: { focus: 'series' }, data: [320, 332, 301, 334, 390, 330, 320] },
    { name: 'Search Engine', type: 'line', stack: 'Total', areaStyle: {}, emphasis: { focus: 'series' }, data: [820, 932, 901, 934, 1290, 1330, 1320] }
  ]
};
```

### Line with Mark Points and Lines
```javascript
option = {
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: [820, 932, 901, 934, 1290, 1330, 1320],
    markPoint: {
      data: [
        { type: 'max', name: 'Max' },
        { type: 'min', name: 'Min' }
      ]
    },
    markLine: {
      data: [{ type: 'average', name: 'Avg' }]
    }
  }]
};
```

### Step Line
```javascript
option = {
  tooltip: { trigger: 'axis' },
  legend: { data: ['Step Start', 'Step Middle', 'Step End'] },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [
    { name: 'Step Start', type: 'line', step: 'start', data: [120, 132, 101, 134, 90, 230, 210] },
    { name: 'Step Middle', type: 'line', step: 'middle', data: [220, 282, 201, 234, 290, 430, 410] },
    { name: 'Step End', type: 'line', step: 'end', data: [450, 432, 401, 454, 590, 530, 510] }
  ]
};
```

### Customized Line Style
```javascript
option = {
  xAxis: { data: ['A', 'B', 'C', 'D', 'E'] },
  yAxis: {},
  series: [{
    data: [10, 22, 28, 23, 19],
    type: 'line',
    lineStyle: { color: '#5470C6', width: 4, type: 'dashed' },
    itemStyle: { borderWidth: 3, borderColor: '#EE6666', color: 'yellow' }
  }]
};
```

### Handling Null/Empty Data
```javascript
option = {
  xAxis: { data: ['A', 'B', 'C', 'D', 'E'] },
  yAxis: {},
  series: [{ data: [10, 22, '-', 23, 19], type: 'line' }]  // '-' creates a gap
};
```

## Bar Charts

### Basic Bar
```javascript
option = {
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{ data: [120, 200, 150, 80, 70, 110, 130], type: 'bar' }]
};
```

### Bar with Background
```javascript
option = {
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{
    data: [120, 200, 150, 80, 70, 110, 130],
    type: 'bar',
    showBackground: true,
    backgroundStyle: { color: 'rgba(180, 180, 180, 0.2)' }
  }]
};
```

### Horizontal Bar (for long labels)
```javascript
option = {
  title: { text: 'Top Products' },
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: ['Product E', 'Product D', 'Product C', 'Product B', 'Product A'] },
  series: [{ type: 'bar', data: [200, 250, 300, 400, 500] }]
};
```

### Grouped Bar Chart
```javascript
option = {
  legend: { data: ['Q1', 'Q2', 'Q3', 'Q4'] },
  xAxis: { type: 'category', data: ['North', 'South', 'East', 'West'] },
  yAxis: { type: 'value' },
  series: [
    { name: 'Q1', type: 'bar', data: [120, 132, 101, 134] },
    { name: 'Q2', type: 'bar', data: [90, 100, 120, 110] },
    { name: 'Q3', type: 'bar', data: [110, 130, 100, 120] },
    { name: 'Q4', type: 'bar', data: [130, 140, 150, 160] }
  ]
};
```

### Stacked Bar Chart
```javascript
option = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['Direct', 'Email', 'Ads', 'Video', 'Search'] },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [
    { name: 'Direct', type: 'bar', stack: 'total', emphasis: { focus: 'series' }, data: [320, 302, 301, 334, 390, 330, 320] },
    { name: 'Email', type: 'bar', stack: 'total', emphasis: { focus: 'series' }, data: [120, 132, 101, 134, 90, 230, 210] },
    { name: 'Ads', type: 'bar', stack: 'total', emphasis: { focus: 'series' }, data: [220, 182, 191, 234, 290, 330, 310] },
    { name: 'Video', type: 'bar', stack: 'total', emphasis: { focus: 'series' }, data: [150, 212, 201, 154, 190, 330, 410] },
    { name: 'Search', type: 'bar', stack: 'total', emphasis: { focus: 'series' }, data: [820, 832, 901, 934, 1290, 1330, 1320] }
  ]
};
```

### Bar with Gradient Color
```javascript
option = {
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{
    data: [120, 200, 150, 80, 70, 110, 130],
    type: 'bar',
    itemStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: '#83bff6' },
        { offset: 0.5, color: '#188df0' },
        { offset: 1, color: '#188df0' }
      ])
    }
  }]
};
```

### Bar with Rounded Corners
```javascript
option = {
  xAxis: { type: 'category', data: ['A', 'B', 'C', 'D', 'E'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: [10, 22, 28, 43, 49],
    itemStyle: { borderRadius: [5, 5, 0, 0] }  // top-left, top-right, bottom-right, bottom-left
  }]
};
```

### Waterfall Chart
```javascript
option = {
  xAxis: { type: 'category', data: ['Total', 'Rent', 'Utilities', 'Transport', 'Meals', 'Other'] },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Placeholder',
      type: 'bar',
      stack: 'Total',
      itemStyle: { borderColor: 'transparent', color: 'transparent' },
      emphasis: { itemStyle: { borderColor: 'transparent', color: 'transparent' } },
      data: [0, 1700, 1400, 1200, 300, 0]
    },
    {
      name: 'Expense',
      type: 'bar',
      stack: 'Total',
      label: { show: true, position: 'inside' },
      data: [2900, 1200, 300, 200, 900, 300]
    }
  ]
};
```

## Pie Charts

### Basic Pie
```javascript
option = {
  tooltip: { trigger: 'item' },
  legend: { top: '5%', left: 'center' },
  series: [{
    type: 'pie',
    radius: '50%',
    data: [
      { value: 1048, name: 'Search Engine' },
      { value: 735, name: 'Direct' },
      { value: 580, name: 'Email' },
      { value: 484, name: 'Union Ads' },
      { value: 300, name: 'Video Ads' }
    ],
    emphasis: {
      itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
    }
  }]
};
```

### Donut Chart
```javascript
option = {
  tooltip: { trigger: 'item' },
  legend: { top: '5%', left: 'center' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: {
      label: { show: true, fontSize: 40, fontWeight: 'bold' }
    },
    labelLine: { show: false },
    data: [
      { value: 1048, name: 'Search Engine' },
      { value: 735, name: 'Direct' },
      { value: 580, name: 'Email' },
      { value: 484, name: 'Union Ads' },
      { value: 300, name: 'Video Ads' }
    ]
  }]
};
```

### Half Donut (Gauge-like)
```javascript
option = {
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['50%', '70%'],
    startAngle: 180,
    endAngle: 360,
    data: [
      { value: 1048, name: 'Search Engine' },
      { value: 735, name: 'Direct' },
      { value: 580, name: 'Email' }
    ]
  }]
};
```

### Nested Pie (Sunburst-like)
```javascript
option = {
  tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: [0, '30%'],
      label: { position: 'inner', fontSize: 14 },
      labelLine: { show: false },
      data: [
        { value: 1548, name: 'Search Engine' },
        { value: 775, name: 'Direct' }
      ]
    },
    {
      name: 'Access From',
      type: 'pie',
      radius: ['45%', '60%'],
      labelLine: { length: 30 },
      data: [
        { value: 1048, name: 'Baidu' },
        { value: 335, name: 'Google' },
        { value: 310, name: 'Bing' },
        { value: 251, name: 'Direct' },
        { value: 234, name: 'Email' },
        { value: 147, name: 'Union Ads' }
      ]
    }
  ]
};
```

### Rose Chart (Nightingale)
```javascript
option = {
  legend: { top: 'bottom' },
  series: [{
    name: 'Nightingale Chart',
    type: 'pie',
    radius: [50, 250],
    center: ['50%', '50%'],
    roseType: 'area',
    itemStyle: { borderRadius: 8 },
    data: [
      { value: 40, name: 'rose 1' },
      { value: 38, name: 'rose 2' },
      { value: 32, name: 'rose 3' },
      { value: 30, name: 'rose 4' },
      { value: 28, name: 'rose 5' }
    ]
  }]
};
```

## Scatter Charts

### Basic Scatter
```javascript
option = {
  xAxis: {},
  yAxis: {},
  series: [{
    type: 'scatter',
    symbolSize: 20,
    data: [
      [10.0, 8.04], [8.07, 6.95], [13.0, 7.58], [9.05, 8.81], [11.0, 8.33],
      [14.0, 7.66], [13.4, 6.81], [10.0, 6.33], [14.0, 8.96], [12.5, 6.82]
    ]
  }]
};
```

### Bubble Chart (Variable Size)
```javascript
option = {
  xAxis: { type: 'value', name: 'GDP (Trillion $)' },
  yAxis: { type: 'value', name: 'Life Expectancy (Years)' },
  tooltip: {
    formatter: (params) => `${params.data[3]}<br/>GDP: $${params.data[0]}T<br/>Life Exp: ${params.data[1]}<br/>Pop: ${(params.data[2]/1e6).toFixed(1)}M`
  },
  series: [{
    type: 'scatter',
    symbolSize: (data) => Math.sqrt(data[2]) / 5000,
    data: [
      // [GDP, Life Expectancy, Population, Country]
      [21.43, 78.5, 331002651, 'USA'],
      [14.72, 76.9, 1439323776, 'China'],
      [5.06, 84.6, 126476461, 'Japan'],
      [3.85, 81.3, 83783942, 'Germany'],
      [2.83, 81.2, 67886011, 'UK']
    ],
    itemStyle: { opacity: 0.7 }
  }]
};
```

### Scatter with Categories
```javascript
option = {
  legend: { data: ['Group A', 'Group B'] },
  xAxis: {},
  yAxis: {},
  series: [
    {
      name: 'Group A',
      type: 'scatter',
      data: [[10, 8], [8, 7], [13, 8], [9, 9], [11, 8]],
      symbolSize: 15
    },
    {
      name: 'Group B',
      type: 'scatter',
      data: [[5, 4], [4, 5], [6, 3], [7, 4], [3, 6]],
      symbolSize: 15
    }
  ]
};
```

### Scatter with Effect (Animation)
```javascript
option = {
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [{
    type: 'effectScatter',
    symbolSize: 20,
    data: [[10, 8], [8, 7], [13, 8], [9, 9]],
    rippleEffect: { brushType: 'stroke' }
  }]
};
```

### Scatter with Custom Symbol
```javascript
option = {
  xAxis: { data: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] },
  yAxis: {},
  series: [{
    type: 'scatter',
    data: [220, 182, 191, 234, 290, 330, 310],
    symbolSize: 20,
    symbol: 'diamond'  // circle, rect, roundRect, triangle, diamond, pin, arrow
  }]
};
```

### Jittered Scatter (v6 - for overlapping points)
```javascript
option = {
  xAxis: { type: 'category', data: ['A', 'B', 'C'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'scatter',
    data: [
      ['A', 10], ['A', 12], ['A', 11], ['A', 10], ['A', 13],
      ['B', 20], ['B', 22], ['B', 21], ['B', 20],
      ['C', 15], ['C', 16], ['C', 14]
    ],
    jitter: { width: 20 },
    jitterOverlap: false
  }]
};
```

## Rich Text Labels

### Basic Rich Text
```javascript
option = {
  series: [{
    type: 'pie',
    radius: '55%',
    label: {
      formatter: '{name|{b}}\n{value|{c}} ({d}%)',
      rich: {
        name: { fontSize: 14, color: '#666' },
        value: { fontSize: 20, fontWeight: 'bold', color: '#333' }
      }
    },
    data: [
      { value: 1048, name: 'Search' },
      { value: 735, name: 'Direct' },
      { value: 580, name: 'Email' }
    ]
  }]
};
```

### Rich Text with Icons/Images
```javascript
option = {
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: [120, 200, 150],
    label: {
      show: true,
      position: 'top',
      formatter: '{icon|} {value|{c}}',
      rich: {
        icon: {
          height: 20,
          width: 20,
          backgroundColor: { image: 'https://echarts.apache.org/examples/data/asset/img/weather/sunny_128.png' }
        },
        value: { fontSize: 14, color: '#333', padding: [0, 0, 0, 5] }
      }
    }
  }]
};
```

### Rich Text with Background and Border
```javascript
option = {
  series: [{
    type: 'pie',
    radius: '50%',
    label: {
      formatter: '{title|{b}}\n{hr|}\n{detail|Value: {c}}',
      backgroundColor: '#F6F8FC',
      borderColor: '#8C8D8E',
      borderWidth: 1,
      borderRadius: 4,
      padding: [5, 10],
      rich: {
        title: { color: '#333', fontSize: 14, fontWeight: 'bold', lineHeight: 24 },
        hr: { borderColor: '#8C8D8E', width: '100%', borderWidth: 1, height: 0 },
        detail: { color: '#666', fontSize: 12, lineHeight: 20 }
      }
    },
    data: [
      { value: 1048, name: 'Search' },
      { value: 735, name: 'Direct' }
    ]
  }]
};
```

### Bar Chart with Rotated Rich Labels
```javascript
option = {
  xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Revenue',
      type: 'bar',
      data: [320, 332, 301, 334, 390],
      label: {
        show: true,
        rotate: 90,
        formatter: '{c} {name|{a}}',
        fontSize: 14,
        rich: { name: { color: '#999', fontSize: 12 } }
      }
    }
  ]
};
```

### Complex Rich Text Layout
```javascript
option = {
  series: [{
    type: 'scatter',
    symbolSize: 1,
    data: [[0, 0]],
    label: {
      show: true,
      formatter: [
        '{titleBg|Dashboard Summary}',
        '{hr|}',
        '  {sunny|} Sunny Days: {value|128}  ',
        '  {cloudy|} Cloudy Days: {value|87}  ',
        '  {rainy|} Rainy Days: {value|52}  '
      ].join('\n'),
      backgroundColor: '#fff',
      borderColor: '#ccc',
      borderWidth: 1,
      borderRadius: 8,
      padding: 10,
      rich: {
        titleBg: {
          backgroundColor: '#4477AA',
          color: '#fff',
          padding: [8, 15],
          borderRadius: [8, 8, 0, 0],
          width: '100%',
          fontSize: 16
        },
        hr: { borderColor: '#ddd', width: '100%', borderWidth: 1, height: 0 },
        sunny: { height: 24, backgroundColor: { image: 'sunny.png' } },
        cloudy: { height: 24, backgroundColor: { image: 'cloudy.png' } },
        rainy: { height: 24, backgroundColor: { image: 'rainy.png' } },
        value: { fontSize: 18, fontWeight: 'bold', color: '#333' }
      }
    }
  }],
  xAxis: { show: false, min: -1, max: 1 },
  yAxis: { show: false, min: -1, max: 1 }
};
```

## Radar Charts

### Basic Radar
```javascript
option = {
  radar: {
    indicator: [
      { name: 'Sales', max: 6500 },
      { name: 'Admin', max: 16000 },
      { name: 'IT', max: 30000 },
      { name: 'Support', max: 38000 },
      { name: 'Dev', max: 52000 },
      { name: 'Marketing', max: 25000 }
    ]
  },
  series: [{
    type: 'radar',
    data: [{ value: [4200, 3000, 20000, 35000, 50000, 18000], name: 'Budget' }]
  }]
};
```

### Multiple Radar Series
```javascript
option = {
  legend: { data: ['Allocated', 'Actual'] },
  radar: {
    indicator: [
      { name: 'Sales', max: 6500 },
      { name: 'Admin', max: 16000 },
      { name: 'Tech', max: 30000 },
      { name: 'Support', max: 38000 },
      { name: 'Dev', max: 52000 }
    ]
  },
  series: [{
    type: 'radar',
    data: [
      { value: [4200, 3000, 20000, 35000, 50000], name: 'Allocated', areaStyle: { opacity: 0.3 } },
      { value: [5000, 14000, 28000, 26000, 42000], name: 'Actual', areaStyle: { opacity: 0.3 } }
    ]
  }]
};
```

## Heatmap

### Calendar Heatmap
```javascript
// Generate data for a year
function generateData() {
  const data = [];
  const start = new Date('2024-01-01');
  const end = new Date('2024-12-31');
  for (let time = start; time <= end; time.setDate(time.getDate() + 1)) {
    data.push([echarts.time.format(time, '{yyyy}-{MM}-{dd}', false), Math.floor(Math.random() * 10)]);
  }
  return data;
}

option = {
  visualMap: { min: 0, max: 10, type: 'piecewise', orient: 'horizontal', left: 'center', top: 65 },
  calendar: { top: 120, left: 30, right: 30, cellSize: ['auto', 13], range: '2024', itemStyle: { borderWidth: 0.5 }, yearLabel: { show: true } },
  series: { type: 'heatmap', coordinateSystem: 'calendar', data: generateData() }
};
```

### Cartesian Heatmap
```javascript
const hours = ['12a', '1a', '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a', '12p', '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', '10p', '11p'];
const days = ['Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday', 'Sunday'];
const data = [[0, 0, 5], [0, 1, 1], [0, 2, 0], [1, 0, 7], [1, 1, 3], [1, 2, 2]]; // [hour, day, value]

option = {
  tooltip: { position: 'top' },
  grid: { height: '50%', top: '10%' },
  xAxis: { type: 'category', data: hours, splitArea: { show: true } },
  yAxis: { type: 'category', data: days, splitArea: { show: true } },
  visualMap: { min: 0, max: 10, calculable: true, orient: 'horizontal', left: 'center', bottom: '15%' },
  series: [{
    name: 'Activity',
    type: 'heatmap',
    data: data,
    label: { show: true },
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
};
```

## Candlestick (Financial)

### Basic Candlestick
```javascript
option = {
  xAxis: { type: 'category', data: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'candlestick',
    // Data format: [open, close, low, high]
    data: [
      [20, 34, 10, 38],
      [40, 35, 30, 50],
      [31, 38, 33, 44],
      [38, 15, 5, 42],
      [20, 30, 15, 35]
    ]
  }]
};
```

### Candlestick with Volume
```javascript
option = {
  grid: [
    { left: '10%', right: '8%', height: '50%' },
    { left: '10%', right: '8%', top: '65%', height: '16%' }
  ],
  xAxis: [
    { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May'], gridIndex: 0 },
    { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May'], gridIndex: 1 }
  ],
  yAxis: [
    { type: 'value', gridIndex: 0 },
    { type: 'value', gridIndex: 1 }
  ],
  series: [
    { type: 'candlestick', xAxisIndex: 0, yAxisIndex: 0, data: [[20, 34, 10, 38], [40, 35, 30, 50], [31, 38, 33, 44], [38, 15, 5, 42], [20, 30, 15, 35]] },
    { type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: [100, 120, 80, 150, 90], itemStyle: { color: '#7fbe9e' } }
  ]
};
```

## Gauge

### Basic Gauge
```javascript
option = {
  series: [{
    type: 'gauge',
    progress: { show: true, width: 18 },
    axisLine: { lineStyle: { width: 18 } },
    axisTick: { show: false },
    splitLine: { length: 15, lineStyle: { width: 2, color: '#999' } },
    axisLabel: { distance: 25, color: '#999', fontSize: 12 },
    anchor: { show: true, showAbove: true, size: 25, itemStyle: { borderWidth: 10 } },
    detail: { valueAnimation: true, fontSize: 40, offsetCenter: [0, '70%'] },
    data: [{ value: 70 }]
  }]
};
```

### Multi-Gauge Dashboard
```javascript
option = {
  series: [
    {
      type: 'gauge',
      center: ['25%', '50%'],
      radius: '60%',
      min: 0,
      max: 100,
      title: { show: true, offsetCenter: [0, '80%'] },
      detail: { valueAnimation: true, offsetCenter: [0, '50%'] },
      data: [{ value: 70, name: 'CPU' }]
    },
    {
      type: 'gauge',
      center: ['75%', '50%'],
      radius: '60%',
      min: 0,
      max: 100,
      title: { show: true, offsetCenter: [0, '80%'] },
      detail: { valueAnimation: true, offsetCenter: [0, '50%'] },
      data: [{ value: 45, name: 'Memory' }]
    }
  ]
};
```

## Funnel

```javascript
option = {
  title: { text: 'Conversion Funnel', left: 'center' },
  tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
  series: [{
    name: 'Funnel',
    type: 'funnel',
    left: '10%',
    width: '80%',
    label: { position: 'inside' },
    labelLine: { show: false },
    itemStyle: { borderColor: '#fff', borderWidth: 1 },
    emphasis: { label: { fontSize: 20 } },
    data: [
      { value: 100, name: 'Visit' },
      { value: 80, name: 'Inquiry' },
      { value: 60, name: 'Add to Cart' },
      { value: 40, name: 'Checkout' },
      { value: 20, name: 'Purchase' }
    ]
  }]
};
```

## Sankey

```javascript
option = {
  series: [{
    type: 'sankey',
    layout: 'none',
    emphasis: { focus: 'adjacency' },
    data: [
      { name: 'Visits' },
      { name: 'Homepage' },
      { name: 'Products' },
      { name: 'Cart' },
      { name: 'Checkout' },
      { name: 'Purchased' },
      { name: 'Bounced' }
    ],
    links: [
      { source: 'Visits', target: 'Homepage', value: 5000 },
      { source: 'Homepage', target: 'Products', value: 3500 },
      { source: 'Homepage', target: 'Bounced', value: 1500 },
      { source: 'Products', target: 'Cart', value: 2000 },
      { source: 'Products', target: 'Bounced', value: 1500 },
      { source: 'Cart', target: 'Checkout', value: 1500 },
      { source: 'Cart', target: 'Bounced', value: 500 },
      { source: 'Checkout', target: 'Purchased', value: 1200 },
      { source: 'Checkout', target: 'Bounced', value: 300 }
    ]
  }]
};
```

## Treemap

```javascript
option = {
  series: [{
    type: 'treemap',
    data: [
      {
        name: 'Technology',
        value: 400,
        children: [
          { name: 'Apple', value: 150 },
          { name: 'Microsoft', value: 120 },
          { name: 'Google', value: 130 }
        ]
      },
      {
        name: 'Finance',
        value: 300,
        children: [
          { name: 'JPMorgan', value: 100 },
          { name: 'Goldman', value: 80 },
          { name: 'Morgan Stanley', value: 120 }
        ]
      },
      {
        name: 'Healthcare',
        value: 200,
        children: [
          { name: 'Pfizer', value: 80 },
          { name: 'Johnson & Johnson', value: 120 }
        ]
      }
    ]
  }]
};
```

## Sunburst

```javascript
option = {
  series: [{
    type: 'sunburst',
    radius: [0, '90%'],
    label: { rotate: 'radial' },
    data: [
      {
        name: 'Technology',
        children: [
          { name: 'Software', value: 20 },
          { name: 'Hardware', value: 15 },
          { name: 'Services', value: 10 }
        ]
      },
      {
        name: 'Finance',
        children: [
          { name: 'Banking', value: 18 },
          { name: 'Insurance', value: 12 }
        ]
      },
      {
        name: 'Healthcare',
        children: [
          { name: 'Pharma', value: 15 },
          { name: 'Biotech', value: 10 }
        ]
      }
    ]
  }]
};
```

## Graph (Network)

```javascript
option = {
  series: [{
    type: 'graph',
    layout: 'force',
    roam: true,
    label: { show: true },
    force: { repulsion: 100 },
    data: [
      { name: 'Node 1', symbolSize: 50 },
      { name: 'Node 2', symbolSize: 40 },
      { name: 'Node 3', symbolSize: 30 },
      { name: 'Node 4', symbolSize: 30 },
      { name: 'Node 5', symbolSize: 25 }
    ],
    links: [
      { source: 'Node 1', target: 'Node 2' },
      { source: 'Node 1', target: 'Node 3' },
      { source: 'Node 1', target: 'Node 4' },
      { source: 'Node 2', target: 'Node 5' },
      { source: 'Node 3', target: 'Node 5' }
    ]
  }]
};
```

## Boxplot

```javascript
option = {
  xAxis: { type: 'category', data: ['Group A', 'Group B', 'Group C', 'Group D'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'boxplot',
    // Data format: [min, Q1, median, Q3, max]
    data: [
      [655, 850, 940, 980, 1070],
      [760, 800, 845, 885, 960],
      [780, 840, 855, 880, 940],
      [720, 767.5, 815, 865, 920]
    ]
  }]
};
```

## Parallel Coordinates

```javascript
option = {
  parallelAxis: [
    { dim: 0, name: 'Price' },
    { dim: 1, name: 'Rating' },
    { dim: 2, name: 'Reviews' },
    { dim: 3, name: 'Category', type: 'category', data: ['A', 'B', 'C'] }
  ],
  series: [{
    type: 'parallel',
    lineStyle: { width: 2, opacity: 0.5 },
    data: [
      [100, 4.5, 200, 'A'],
      [80, 4.2, 150, 'B'],
      [120, 4.8, 300, 'A'],
      [90, 3.9, 180, 'C']
    ]
  }]
};
```

## ECharts v6 New Features

### Chord Chart (v6)
```javascript
option = {
  series: [{
    type: 'chord',
    data: [
      { name: 'A', value: 100 },
      { name: 'B', value: 80 },
      { name: 'C', value: 60 }
    ],
    links: [
      { source: 'A', target: 'B', value: 30 },
      { source: 'A', target: 'C', value: 20 },
      { source: 'B', target: 'C', value: 25 }
    ]
  }]
};
```

### Dynamic Theme Switching (v6)
```javascript
const chart = echarts.init(container);
chart.setOption(option);

// Switch theme at runtime without reinitializing
chart.setTheme('dark');

// Or respond to system theme changes
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
mediaQuery.addEventListener('change', (e) => {
  chart.setTheme(e.matches ? 'dark' : 'light');
});
```

### Using v5 Colors in v6
```javascript
// v6 has a new default theme. To use v5 color palette:
const v5Colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'];
option = { color: v5Colors, /* ... */ };
```
