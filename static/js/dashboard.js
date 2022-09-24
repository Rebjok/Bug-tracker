/* globals Chart:false, feather:false */

(() => {
  'use strict'

  feather.replace({ 'aria-hidden': 'true' })

   //SECOND ROW
   // Priority Project Pie Chart

  const priorityPie = document.getElementById('pieChart')

  const pieChart = new Chart(priorityPie, {
    type: 'pie',
    data: {
      labels: [
        'Urgent',
        'High',
        'Medium',
        'Low'
      ],
      datasets: [{
        label: 'My First Dataset',
        data: priorityProjectData,
        backgroundColor: [
          'rgb(255, 99, 132)',
          'rgb(54, 162, 235)',
          'rgb(255, 205, 86)',
          'rgba(75, 192, 192, 1)'
        ],
        hoverOffset: 4
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            display: false
          },
          gridLines : {
            display : false
            }
        }]
      },
      legend: {
        display: true
      }
    }
  })

    //Project Distribution Bar Chart
    const distributionBar = document.getElementById('barChart').getContext('2d');
    const barChart = new Chart(distributionBar, {
        type: 'bar',
        data: {
            labels: ['P1', 'P2', 'P3', 'P4', 'P5', 'P6'],
            datasets: [{
                label: 'Users',
                data: distributionBarData[0],
                backgroundColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                stack: 'Stack 0'
            },
            {
                label: 'Developers',
                data: distributionBarData[1],
                backgroundColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                stack: 'Stack 0'
            },
            {
                label: 'Project Managers',
                data: distributionBarData[2],
                backgroundColor: [
                    'rgba(255, 206, 86, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(255, 206, 86, 1)',
                ],
                stack: 'Stack 0'
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            legend: {
                display: true
            },
            responsive: true,
            scales: {
              x: {
                stacked: true,
              },
              y: {
                stacked: true
              }
            }
        }
    });


    //THIRD ROW
    //project distribution pie chart
    const distributionPie = document.getElementById('distributionPie')

      const distributionPieChart = new Chart(distributionPie, {
        type: 'pie',
        data: {
          labels: ticketDistributionTitles,
          datasets: [{
            label: 'My First Dataset',
            data: ticketDistributionPieData,
            backgroundColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(255, 159, 64, 1)',
              'rgba(255, 205, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(201, 203, 207, 1)'
            ],
            hoverOffset: 4
          }]
        },
        options: {
          scales: {
            yAxes: [{
              ticks: {
                display: false
              },
              gridLines : {
                display : false
                }
            }]
          },
          legend: {
            display: true
          }
        }
      })

      //project distribution donut chart
    const distributionDonut = document.getElementById('distributionDonut')

      const distributionDonutChart = new Chart(distributionDonut, {
        type: 'doughnut',
        data: {
          labels: [
            'High',
            'Medium',
            'Low'
          ],
          datasets: [{
            label: 'My First Dataset',
            data: [300, 0, 0],
            backgroundColor: [
              'rgb(255, 99, 132)',
              'rgb(54, 162, 235)',
              'rgb(255, 205, 86)'
            ],
            hoverOffset: 4
          }]
        },
        options: {
          scales: {
            yAxes: [{
              ticks: {
                display: false
              },
              gridLines : {
                display : false
                }
            }]
          },
          legend: {
            display: true
          }
        }
      })

      //Project History Line Chart
      const historyLineChart = document.getElementById('historyLine')
      const historyLine = new Chart(historyLineChart, {
        type: 'line',
        data: {
          labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6'],
          datasets: [
            {
              label: 'Dataset',
              data: [40,100,22,58,89,11],
              borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
              fill: false,
              stepped: true,
            }
          ]
        },
        options: {
            scales: {
                y: {
                    stacked: true
                }
            },
            responsive: true,
            interaction: {
              intersect: false,
              axis: 'x'
            },
            legend: {
                display: false
              }
          },
      })



})()