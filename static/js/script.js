// Placeholder for custom JavaScript code.
console.log("Car Comparison App loaded.");

// Chart.js Code for Car Comparison Chart
document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('carComparisonChart').getContext('2d');

    // Car data passed from Flask (make sure this matches the variable in results.html)
    const carData = JSON.parse('{{ cars_data | tojson | safe }}');

    const carLabels = carData.map(car => car.company);
    const performanceScores = carData.map(car => car.perf_score);
    const valueScores = carData.map(car => car.value_score);

    const carChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: carLabels,
            datasets: [
                {
                    label: 'Performance Score',
                    data: performanceScores,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',  // Blue
                    borderColor: 'rgba(41, 128, 185, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Value Score',
                    data: valueScores,
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',  // Green
                    borderColor: 'rgba(39, 174, 96, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
