import 'regenerator-runtime/runtime';
import axios from 'axios';

//const res = axios.get()

var map = L.map('map').setView([51.505, -0.09], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var marker1 = L.marker([51.5, -0.09]).addTo(map);
var marker2 = L.marker([55.5, -9.09]).addTo(map);
var marker3 = L.marker([43.30, -0.36]).addTo(map);

marker1.bindPopup("GPS n°1")
marker2.bindPopup("GPS n°2")
marker3.bindPopup("GPS n°3")