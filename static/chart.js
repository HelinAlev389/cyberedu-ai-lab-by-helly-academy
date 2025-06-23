document.addEventListener("DOMContentLoaded", function () {
  const chartDataEl = document.getElementById("chartData");
  if (!chartDataEl) return;  // ако няма данни

  const chartData = JSON.parse(chartDataEl.textContent || '{}');

  const ctx = document.getElementById("logChart");
  if (!ctx) return;

  new Chart(ctx.getContext("2d"), {
    type: "bar",
    data: {
      labels: chartData.labels || [],
      datasets: [{
        label: "# на събития",
        data: chartData.values || [],
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              const index = context.dataIndex;
              const tooltip = chartData.tooltips?.[index] || "";
              return [`Събития: ${context.formattedValue}`, tooltip];
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: "Брой събития" }
        }
      }
    }
  });
});
