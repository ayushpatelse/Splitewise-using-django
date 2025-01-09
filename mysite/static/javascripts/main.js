function delete_ask(){
    var name = document.getElementById('confirmationModal')
    name.classList.remove('hidden')
    console.log('functino called')
}
const ctx = document.getElementById('myChart');

new Chart(ctx, {
type: 'bar',
data: {
  labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
  datasets: [{
    label: '# of Votes',
    data: [12, 19, 3, 5, 2, 3],
    borderWidth: 1
  }]
},
options: {
  scales: {
    y: {
      beginAtZero: true
    }
  }
}
});

