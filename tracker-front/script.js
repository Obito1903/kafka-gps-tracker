import 'regenerator-runtime/runtime';

var map = L.map('map').setView([46.227638, 2.213749], 6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const socket = new WebSocket("ws://api:80/ws")

socket.addEventListener("open", () => {
    console.log("WS oppened")
})

socket.addEventListener("message", (event) => {
    let res = JSON.parse(event.data);
    L.marker([res["lat"], res["lng"]]).addTo(map).bindPopup(res["name"]);
});
