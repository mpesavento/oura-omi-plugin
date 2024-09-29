document.addEventListener('DOMContentLoaded', function() {
    let currentHRChart = null;

    console.log('DOM Content Loaded');

    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    } else {
        console.log('Chart.js is loaded successfully');
    }

    const form = document.getElementById('dateForm');
    const readinessScoreElement = document.getElementById('readiness-score');
    const sleepScoreElement = document.getElementById('sleep-score');
    const sleepPeriodElement = document.getElementById('sleep-period');
    const activityScoreElement = document.getElementById('activity-score');
    const dateMessageElement = document.getElementById('date-message');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const selectedDate = formData.get('selected_date');

        // Display that the query was submitted
        dateMessageElement.textContent = `Fetching data for ${selectedDate}...`;
        dateMessageElement.style.display = 'block';

        try {
            const response = await fetch('/api/get_oura_data', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Display selected date message
            displayDateMessage(selectedDate);

            // Display scores and sleep period
            readinessScoreElement.textContent = data.readiness ? data.readiness.score : 'N/A';
            sleepScoreElement.textContent = data.sleep ? data.sleep.score : 'N/A';
            displaySleepPeriod(data.sleepPeriod);
            activityScoreElement.textContent = data.activity ? data.activity.score : 'N/A';

            // Create heart rate chart
            createHeartRateChart('heartRateChart', data.heartRate, data.sleepPeriod);

        } catch (error) {
            console.error('Error:', error);
            dateMessageElement.textContent = `Error: ${error.message}`;
        }
    });

    function displayDateMessage(selectedDate) {
        const formattedDate = moment(selectedDate).format('dddd, MMMM D, YYYY');
        dateMessageElement.textContent = `Viewing data for ${formattedDate}`;
        dateMessageElement.style.display = 'block';
    }

    function displaySleepPeriod(sleepPeriod) {
        if (sleepPeriod && sleepPeriod.bedtime_start && sleepPeriod.bedtime_end) {
            const startTime = moment(sleepPeriod.bedtime_start).format('HH:mm');
            const endTime = moment(sleepPeriod.bedtime_end).format('HH:mm');
            sleepPeriodElement.textContent = `Sleep Period: ${startTime} - ${endTime}`;
        } else {
            sleepPeriodElement.textContent = 'Sleep Period: N/A';
        }
    }

    function createHeartRateChart(elementId, heartRateData, sleepPeriod) {
        console.log('Creating heart rate chart');
        const ctx = document.getElementById(elementId).getContext('2d');

        // Destroy existing chart if it exists
        if (currentHRChart) {
            currentHRChart.destroy();
            currentHRChart = null;  // Set to null after destroying
        }

        // Prepare data for the chart
        const data = heartRateData.map(d => ({
            x: moment(d.timestamp),
            y: d.bpm
        }));

        // Find min and max BPM for y-axis scaling
        const minBPM = Math.min(...data.map(d => d.y));
        const maxBPM = Math.max(...data.map(d => d.y));
        const yAxisMin = Math.max(0, minBPM - 10);
        const yAxisMax = maxBPM + 10;

        // Create datasets
        const datasets = [
            {
                label: 'Heart Rate',
                data: data,
                borderColor: 'red',
                tension: 0.1,
                pointRadius: 0
            }
        ];

        // Add sleep period as a separate dataset
        if (sleepPeriod.bedtime_start && sleepPeriod.bedtime_end) {
            datasets.push({
                label: 'Sleep Period',
                data: [
                    {x: moment(sleepPeriod.bedtime_start), y: yAxisMin},
                    {x: moment(sleepPeriod.bedtime_start), y: yAxisMax},
                    {x: moment(sleepPeriod.bedtime_end), y: yAxisMax},
                    {x: moment(sleepPeriod.bedtime_end), y: yAxisMin}
                ],
                backgroundColor: 'rgba(128, 128, 128, 0.2)',
                borderColor: 'rgba(128, 128, 128, 0.5)',
                fill: true,
                pointRadius: 0,
                showLine: false
            });
        }

        // Create new chart
        currentHRChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'hour',
                            displayFormats: {
                                hour: 'HH:mm'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        min: yAxisMin,
                        max: yAxisMax,
                        title: {
                            display: true,
                            text: 'BPM'
                        }
                    }
                }
            }
        });
        console.log('Heart rate chart created');
    }
});
