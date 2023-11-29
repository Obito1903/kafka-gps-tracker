import 'regenerator-runtime/runtime';
import axios from 'axios';


var map = L.map('map').setView([46.227638, 2.213749], 6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

//const socket = new WebSocket("ws://localhost:8080")
axios.get("http://192.168.155.3:8000/get-gps-data")
.then((res) => {
    for (let index = 0; index < res.data.length; index++) {
        L.marker([res.data[index].lat, res.data[index].lng]).addTo(map).bindPopup(res.data[index].name);
        
    }
})
.catch((error) => {
    console.log(error)
})

// socket.addEventListener("message", (event) => {
//     console.log("Message from server ", event.data);
//   });
