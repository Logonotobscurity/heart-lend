// Visualization configuration
const config = {
    width: 800,
    height: 600,
    margin: { top: 20, right: 20, bottom: 30, left: 40 },
    colors: d3.schemeTableau10
};

// Get thread ID from URL
const threadId = window.location.pathname.split('/').pop();

// Initialize visualizations when document is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!threadId) {
        showError('No thread ID provided');
        return;
    }

    // Fetch visualization data
    fetch(`/api/visualization/${threadId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            createVisualizations(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to load visualization data');
        });
});

function showError(message) {
    const containers = document.querySelectorAll('.visualization-container');
    containers.forEach(container => {
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    });
}

function createVisualizations(data) {
    createInteractionGraph(data);
    createPatternChart(data.patterns);
    createDepthChart(data.depth_progression);
}

function createInteractionGraph(data) {
    const container = d3.select('#interaction-graph');
    const width = container.node().getBoundingClientRect().width;
    const height = 400;

    // Clear previous content
    container.html('');

    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', [0, 0, width, height]);

    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
        .selectAll('line')
        .data(data.links)
        .join('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.value));

    const node = svg.append('g')
        .selectAll('g')
        .data(data.nodes)
        .join('g')
        .call(drag(simulation));

    node.append('circle')
        .attr('r', 8)
        .attr('fill', (d, i) => config.colors[i % config.colors.length]);

    node.append('text')
        .attr('x', 12)
        .attr('y', '.31em')
        .text(d => d.id)
        .attr('fill', 'currentColor');

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });
}

function createPatternChart(patterns) {
    const container = d3.select('#pattern-chart');
    const width = container.node().getBoundingClientRect().width;
    const height = 300;

    // Clear previous content
    container.html('');

    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

    const margin = { top: 20, right: 20, bottom: 60, left: 40 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const x = d3.scaleBand()
        .range([0, chartWidth])
        .padding(0.1);

    const y = d3.scaleLinear()
        .range([chartHeight, 0]);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    x.domain(patterns.map(d => d.pattern));
    y.domain([0, d3.max(patterns, d => d.count)]);

    g.append('g')
        .attr('transform', `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end');

    g.append('g')
        .call(d3.axisLeft(y));

    g.selectAll('.bar')
        .data(patterns)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.pattern))
        .attr('y', d => y(d.count))
        .attr('width', x.bandwidth())
        .attr('height', d => chartHeight - y(d.count))
        .attr('fill', (d, i) => config.colors[i % config.colors.length]);
}

function createDepthChart(depthData) {
    const container = d3.select('#depth-chart');
    const width = container.node().getBoundingClientRect().width;
    const height = 200;

    // Clear previous content
    container.html('');

    const svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);

    const margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime()
        .range([0, chartWidth])
        .domain(d3.extent(depthData, d => new Date(d.timestamp)));

    const y = d3.scaleLinear()
        .range([chartHeight, 0])
        .domain([0, 3]);

    const line = d3.line()
        .x(d => x(new Date(d.timestamp)))
        .y(d => y(d.depth))
        .curve(d3.curveMonotoneX);

    g.append('g')
        .attr('transform', `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x));

    g.append('g')
        .call(d3.axisLeft(y));

    g.append('path')
        .datum(depthData)
        .attr('fill', 'none')
        .attr('stroke', 'var(--bs-primary)')
        .attr('stroke-width', 2)
        .attr('d', line);
}

// Drag functionality for nodes
function drag(simulation) {
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
}
