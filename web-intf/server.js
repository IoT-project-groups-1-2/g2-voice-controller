'use strict'

//Getting node modules
const express = require('express');
const path = require('path');

const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

//Defining constants
const PORT = process.env.PORT || 3000;

app.get('/', async (req, res) => {
    res.render('home');
});


app.listen(PORT);






