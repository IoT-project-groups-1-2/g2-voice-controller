'use strict'

//Getting node modules
const express = require('express');
const path = require('path');

const app = express();

//Defining constants
const PORT = process.env.PORT || 3000;

app.get('/', async (req, res) => {
    res.send("AYYO WHATZ GUD!");
});


app.listen(PORT);