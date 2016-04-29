var defaultMargins = {top: 10, left: 10, right: 10, bottom: 40};

function clone(object) {
  return JSON.parse(JSON.stringify(object))
}

function appendFilterControls(chart, showCurrentFilters) {
  var controls = chart.root()
      .append('div')
      .classed('filter-controls', true);

  controls
    .append('a')
    .classed('reset', true)
    .attr('style', 'visibility: hidden')
    .attr('href', 'javascript:;')
    .on('click', function() {
      chart.filterAll();
      dc.redrawAll();
    })
    .text('reset');

  if (showCurrentFilters) {
    controls
      .append('span')
      .classed('reset', true)
      .attr('style', 'visibility: hidden')
      .text('Current filter: ')
      .append('span')
      .classed('filter', true)
  }
}

function pluckedDimensionAndGroup(ndx, propname) {
  var dimension = ndx.dimension(plucker(propname));
  return {
    dimension: dimension,
    group: dimension.group()
  };
}

function createRowChart(ndx, selector, propname) {
  var axis = pluckedDimensionAndGroup(ndx, propname);
  var chart = dc.rowChart(selector);
  appendFilterControls(chart);
  chart
    .width(180)
    .height(30 * axis.group.size())
    .margins(defaultMargins)
    .group(axis.group)
    .dimension(axis.dimension)
    .elasticX(true)
    .xAxis().ticks(4);
  return {
    chart: chart,
    dimension: axis.dimension,
    group: axis.group
  };
}

function createPieChart(ndx, selector, propname) {
  var axis = pluckedDimensionAndGroup(ndx, propname);
  var chart = dc.pieChart(selector);
  appendFilterControls(chart);
  chart
    .width(180)
    .height(180)
    .radius(80)
    .dimension(axis.dimension)
    .group(axis.group);
  return {
    chart: chart,
    dimension: axis.dimension,
    group: axis.group
  };
}

function createMonthlyVolumeChart(ndx, selector, seriesGroup, seriesProp) {
  var dateDimension = ndx.dimension(function(d) {
    return d3.time.month(d.application_updated_at_date);
  });

  var margins = clone(defaultMargins);
  margins.left = 40;
  var chart = dc.lineChart(selector);
  appendFilterControls(chart, true);
  chart
    .renderArea(true)
    .width(990)
    .height(200)
    .transitionDuration(1000)
    .margins(margins)
    .dimension(dateDimension)
    .mouseZoomable(false)
    .x(d3.time.scale().domain([new Date(2015, 10, 1), new Date()]))
    .round(d3.time.month.round)
    .xUnits(d3.time.months)
    .elasticY(true)
    .renderHorizontalGridLines(true)
    .legend(dc.legend().x(800).y(10).itemHeight(13).gap(5))
    .brushOn(true)

  seriesGroup.all().forEach(function(d, i) {
    var seriesName = d.key;
    var group = dateDimension.group().reduceSum(function(d) {
      return d[seriesProp] === seriesName ? 1 : 0;
    });
    if (i === 0) {
      chart
        .group(group, seriesName)
    } else {
      chart
        .stack(group, seriesName)
    }
  });
  return {
    chart: chart,
    dimension: dateDimension
  }
}

// http://stackoverflow.com/questions/17524627/is-there-a-way-to-tell-crossfilter-to-treat-elements-of-array-as-separate-record
function createTagsGroup(dimension, scorecardRecs, filterByRec) {
  var reduceAddTags = function(p, v) {
    var recName = v.scorecard_recommendation;
    if (filterByRec && filterByRec !== recName) {
      return p;
    }
    v.scorecard_tags.forEach (function(val, idx) {
      p[val] = (p[val] || {});
      p[val].count = (p[val].count || 0) + 1;
      p[val].score = (p[val].score || 0) + scorecardRecs[recName];
    });
    return p;
  }

  var reduceRemoveTags = function(p, v) {
    var recName = v.scorecard_recommendation;
    if (filterByRec && filterByRec !== recName) {
      return p;
    }
    v.scorecard_tags.forEach (function(val, idx) {
      p[val] = (p[val] || {});
      p[val].count = (p[val].count || 0) - 1;
      p[val].score = (p[val].score || 0) - scorecardRecs[recName];
    });
    return p;
  }

  var reduceInitialTags = function() {
    return {};
  }

  var group = dimension
      .groupAll()
      .reduce(reduceAddTags, reduceRemoveTags, reduceInitialTags)
      .value();

  // hack to make dc.js charts work
  var all = function() {
    return Object.keys(group).map(function(tag) {
      return {
        key: tag,
        value: group[tag].count,
        score: group[tag].score
      };
    });
  }

  var top = function(count) {
    var groups = all();
    groups.sort(function(a, b){return b.score - a.score});
    return groups.slice(0, count);
  };

  return {
    all: all,
    top: top
  };
}

function createTagRecsGroup(dimension, scorecardRecs, byRecs) {
  var reduceAddTags = function(p, v) {
    var recName = v.scorecard_recommendation;
    (v.scorecard_tags || []).forEach (function(val, idx) {
      p[val] = (p[val] || {});
      p[val][recName] = (p[val][recName] || 0) + 1;
      p[val].count = (p[val].count || 0) + 1;
    });
    return p;
  }

  var reduceRemoveTags = function(p, v) {
    var recName = v.scorecard_recommendation;
    v.scorecard_tags.forEach (function(val, idx) {
      p[val] = (p[val] || {});
      p[val][recName] = (p[val][recName] || 0) - 1;
      p[val].count = (p[val].count || 0) - 1;
    });
    return p;
  }

  var reduceInitialTags = function() {
    return {};
  }

  // hack to make dc.js charts work
  var all = function() {
    var reducedGroups = dimension
        .groupAll()
        .reduce(reduceAddTags, reduceRemoveTags, reduceInitialTags)
        .value();
    var allGroups = [];
    Object.keys(reducedGroups).forEach(function(tag) {
      if (byRecs) {
        Object.keys(reducedGroups[tag]).forEach(function(rec) {
          if (rec === 'count') {
            return;
          }
          allGroups.push({
            key: rec + ':' + tag,
            tag: tag,
            rec: rec,
            value: reducedGroups[tag][rec]
          });
        });
      } else {
        var recsAndCount = reducedGroups[tag];
        recsAndCount.key = tag;
        recsAndCount.tag = tag;
        allGroups.push(recsAndCount);
      }
    });
    if (byRecs) {
      allGroups.sort(function(a, b){
        return scorecardRecs[a.rec] - scorecardRecs[b.rec];
      });
    } else {
      allGroups.sort(function(a, b){return a.count - b.count});
    }
    return allGroups;
  }

  var top = function(count) {
    var groups = all();
    return groups.slice(0, count);
  };
  return {
    all: all,
    top: top
  };
}

function bubbleColorScale(scorecardRecs, sortedRecs, maxRadiusValue) {
  var xColorScale = d3.scale.linear()
      .domain([scorecardRecs[sortedRecs[0]], scorecardRecs[sortedRecs[sortedRecs.length - 1]]])
      .range(["#8E62A7", "#3BD867"]); // purle, green
  var yColorScales = {}
  var createYColorScale = function(maxColor) {
    return d3.scale
      .linear()
      .domain([1, maxRadiusValue])
      .range([d3.hsl(maxColor).brighter(1.5), maxColor]);
  }
  return function(d) {
    var maxColor = xColorScale(scorecardRecs[d.rec]);
    var yColorScale = yColorScales[maxColor] = yColorScales[maxColor] || createYColorScale(maxColor);
    return yColorScale(d.value);
  }
}


function createRecsByTagChart(ndx, selector, scorecardRecs) {
  var tagsDimension = ndx.dimension(plucker('scorecard_tags'));
  var tagRecsGroup = createTagRecsGroup(tagsDimension, scorecardRecs, true);

  var yDomain = function() {
    return createTagsGroup(tagsDimension, scorecardRecs)
      .top(Infinity)
      .map(plucker('key'));
  }

  var sortedRecs = Object.keys(scorecardRecs)
      .sort(function(a, b) {
        return scorecardRecs[a] - scorecardRecs[b];
      });

  var maxRadiusValue = Math.max.apply(
    null,
    tagRecsGroup.all().map(function(tagRecs) {
      return tagRecs.value;
    }));
  var colorScale = bubbleColorScale(scorecardRecs, sortedRecs, maxRadiusValue);
  var height = 800;
  var margins = clone(defaultMargins);
  margins.left = 80;

  var chart = dc.bubbleChart(selector);
  appendFilterControls(chart, true);
  chart
    .width(260)
    .height(height)
    .margins(margins)
    .dimension(tagsDimension)
    .group(tagRecsGroup)
    .elasticX(false) // needed to preserve x ordering
    .renderVerticalGridLines(true)
    .maxBubbleRelativeSize(1 / (sortedRecs.length + 2) / 2)
    .filterHandler(function (dimension, filters) {
      dimension.filter(null);
      if (filters.length === 0) {
        dimension.filter(null);
      } else {
        var tagFilters = filters.map(function(key) {
          return key.split(':')[1];
        });
        dimension.filterFunction(function (d) {
          for (var i=0; i < d.length; i++) {
            if (tagFilters.indexOf(d[i]) >= 0) return true;
          }
          return false;
        });
      }
      return filters;
    })
    .colors(colorScale)
    .colorAccessor(function (p) {
      return p;
    })
    .keyAccessor(function (p) {
      return p.rec;
    })
    .valueAccessor(function (p) {
      return p.tag;
    })
    .radiusValueAccessor(function (p) {
      return p.value;
    })
    .label(function (p) {
      return p.value;
    })
    .y(d3.scale.ordinal().domain(yDomain()))
    .xUnits(dc.units.ordinal)
    .x(d3.scale.ordinal().domain(sortedRecs))
    .r(d3.scale.linear().domain([0, maxRadiusValue]))

  dc.override(chart, "_prepareYAxis", function(g) {
    this.__prepareYAxis(g);
    this.y().rangeBands([this.yAxisHeight(), 0]);
  });

  // hack to adjust axes positioning
  chart.on('renderlet', function(g) {
    var xShift = (chart.width() / (sortedRecs.length + 2)) * 0.5 * 0.75 /* magic */;
    var yShift = (chart.height() / (chart.y().domain().length + 2)) * 0.5 * 1.18 /* magic */;
    g.select('.axis.y')
      .attr(
        'transform',
        'translate(' + margins.left + ',' + (margins.top - yShift) + ')');
    g.select('.axis.x')
      .attr(
        'transform',
        'translate(' + (margins.left - xShift) + ',' + (height - margins.bottom) + ')');
    g.selectAll('.axis.x text')
      .attr('transform', 'translate(-10,10) rotate(315)');
  });

  var updateYDomain = function() {
    chart.y().domain(yDomain());
    chart.rescale();
    chart.redraw();
  }

  return {
    chart: chart,
    dimension: tagsDimension,
    group: tagRecsGroup,
    updateYDomain: updateYDomain
  };
}

function createDatatable(ndx, selector) {
  var dimension = ndx.dimension(function(d) {
    return d.application_updated_at_date;
  });
  var chart = dc.dataTable(selector);
  chart
    .dimension(dimension)
    .group(function (d) {
      var format = d3.format('02d');
      var date = d.application_updated_at_date;
      return date.getFullYear() + '/' + format((date.getMonth() + 1));
    })
    .size(Infinity)
    .columns([
      column('Interviewer', 'interviewer_name'),
      column('Job', 'job_title'),
      column('Type', 'interview_type'),
      column('Scorecard', 'scorecard_recommendation'),
      column('Status', 'application_status'),
      column('Tags', 'scorecard_tags'),
    ])
    .sortBy(function (d) {
      return d.application_updated_at_date;
    })
    .order(d3.descending);

  return {
    chart: chart,
    dimension: dimension
  };
}

function column(label, prop) {
  return {
    label: label,
    format: plucker(prop)
  };
}

function main(data) {
  data.interviews.forEach(function(d) {
    d.application_updated_at_date = d3.time.format.iso.parse(d.application_updated_at);
  });
  var ndx = crossfilter(data.interviews);
  var all = ndx.groupAll();

  var jobTitles = createRowChart(ndx, '#job-title-chart', 'job_title')
  jobTitles
    .chart
    .ordinalColors(qualitativeColors(5));
  createRowChart(ndx, '#interviewer-chart', 'interviewer_name')
    .chart
    .ordinalColors(qualitativeColors(12));
  createRowChart(ndx, '#interview-type-chart', 'interview_type')
    .chart
    .ordering(function(d) {
      return -d.value;
    });
  createRowChart(ndx, '#scorecard-outcome-chart', 'scorecard_recommendation')
    .chart
    .ordering(function(d) {
      return data.scorecard_recs[d.key];
    });
  createPieChart(ndx, '#overall-outcome-chart', 'application_status');

  createMonthlyVolumeChart(ndx, '#volume-by-month-chart', jobTitles.group, 'job_title');
  var recsByTag = createRecsByTagChart(ndx, '#recs-by-tag-chart', data.scorecard_recs);

  createDatatable(ndx, '#datatable');

  dc.chartRegistry.list().forEach(function(chart) {
    if (recsByTag.chart.anchorName() === chart.anchorName()) {
      return;
    }
    chart.on('filtered', recsByTag.updateYDomain);
  })

  dc.renderAll();
}

function qualitativeColors(num) {
  return palette('tol', num).map(function(d) { return '#' + d; })
}

function plucker(key) {
  return function(d) {
    return d[key];
  }
}

d3.json('interviews.json', main);
