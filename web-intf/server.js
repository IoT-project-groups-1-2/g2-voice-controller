'use strict'

//Getting node modules
const express = require('express');
const path = require('path');
const mqtt = require('mqtt');
const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

//Defining constants
const PORT = process.env.PORT || 3000;
const broker_url = 'mqtt://127.0.0.1:1883';
const client = mqtt.connect(broker_url, { clientId: 'node', clean: true });
const settings_topic = "controller/settings";
const status_topic = "controller/status";

client.subscribe(status_topic, (err) => {
    console.log("status topic subscribed.")
    if (!err) {
        client.publish(status_topic, 'Hello mqtt');

    }
});

app.get('/', async (req, res) => {
    res.render('home');
});

app.get('/voice-data',(req, res) => {

    client.on('message', (topic, msg) => {
        client.removeAllListeners();
        msg = msg.toString();
        console.log(msg);
        return res.json(msg);
    });
    res.send('sucks');

});




app.listen(PORT);






