'use strict'

//Getting node modules
const express = require('express');
const app = express();
const path = require('path');
const mqtt = require('mqtt');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const {hashPassword, verifyPassword} = require("./pbkdf2");
const {playlist, addSong} = require("./api")
const http = require('http');
const server = http.createServer(app);
const {Server} = require("socket.io");
const fs = require("fs");
const songs = require("./songs.json");
const io = new Server(server);
const MongoClient = require('mongodb').MongoClient;


/* MIDDLEWARES */

app.use(bodyParser.urlencoded({extended: true}));
app.use(cookieParser());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));


/* DEFINING CONSTRAINTS */
const PORT = process.env.PORT || 3000;

const broker_url = 'mqtt://broker.hivemq.com:1883';
const mongo_url = 'mongodb://localhost:27017';
const client = mqtt.connect(broker_url);
const web_topic = "rtttl/wtd";
const device_topic = "rtttl/dtw";
const mod_topic = "rtttl/mod"


// CONNECTING TO THE MQTT SERVER AND SUBSCRIBING TO THE TOPICS
client.on('connect', function () {
    client.subscribe(web_topic);
    client.subscribe(device_topic);
    client.subscribe(mod_topic);


});


// Connecting to the websockets and will send to the mqtt topic once message is received by the websocket
io.on('connection', (socket) => {
    setInterval(() => {
        client.on('message', (topic, msg) => {
            client.removeAllListeners();
            msg =
                msg.toString();
            io.emit('rtttl', msg);
        });

    }, 8000)


    socket.on("songs", (arg) => {
        client.publish(web_topic, arg, {qos: 0, retain: false}, (error) => {
            if (error) {
                console.error(error);
            }
        })
    })
});


//Rendering to the login page
app.get('/', async (req, res) => {
    res.render("login");

});

//Rendering to the signup page
app.get('/signup', (req, res) => {
    if (req.cookies.loggedIn === "true") return res.redirect('/home');
    res.render('signup');
});

//Rendering to the home page
app.get('/home', (req, res) => {
    if (req.cookies.loggedIn === "false") return res.redirect('/');
    res.render('home');
});


//logout route and redirects to the login page
app.get('/logout', (req, res) => {
    if (req.cookies.loggedIn === "true") {
        res.cookie("curr_user", "");
        res.cookie("loggedIn", false);
    }
    res.redirect('/home');
});

//Rendering to the songlist page
app.get('/commands', (req, res) => {
    if (req.cookies.loggedIn === "false") return res.redirect('/');
    res.render('command');

});

//Sending the songlist in json type
app.get('/api/songs', async (req, res) => {
    res.json(playlist);

})

//Rendering to the add page to add songs
app.get('/add', async (req, res) => {
    if (req.cookies.loggedIn === "false") return res.redirect('/');
    res.render('add');
})


//Post method to check if the user data duplicates the data in the database
app.post('/signup', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    hashPassword(password).then(hashedPassword => {
        const newUser = {username, hashedPassword};
        addUser(newUser).then(msg => {
            res.cookie("login_err", 201);
            res.redirect('/');
        })
            .catch(err_msg => {
                res.cookie("login_err", 406);
                res.redirect('/');
            });
    }).catch(err => {
        res.cookie("login_err", 503);
        res.redirect('/');
    });
});


//post method to check if the login credentials match the data in the database.

app.post('/login', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    let query_obj = {username: username};
    MongoClient.connect(mongo_url, function (err, db) {
        if (err) throw err;
        const dbo = db.db("users");
        dbo.collection("users").find(query_obj).toArray((err, user_arr) => {
            const user = user_arr[0];
            if (user !== undefined) {
                //checking if the inputted password matches the password from the database
                verifyPassword(password, user.hashedPassword)
                    .then((equal) => {

                        if (equal) {
                            res.statusCode =
                                200;
                            if (req.cookies.curr_user !== user.username) {
                                res.cookie("curr_user", user.username);
                                res.cookie("loggedIn", true);

                            }
                            res.cookie("login_err", 200);
                            return res.redirect('/home');
                        } else {
                            res.cookie("login_err", 401);
                            return res.redirect('/');
                        }
                    })
                    .catch((err_msg) => {
                        res.cookie("login_err", 401);
                        return res.redirect('/');
                    });
            } else {
                res.cookie("login_err", 401);
                return res.redirect('/');
            }
        });
    });
});

//Post method to add the song into the songlist
app.post('/add/song', (req, res) => {
    const name = req.body.name;
    const rtttl = req.body.rtttl;
    const id = Number(songs[songs.length-1].id) + 1;
    const newSong = {Name: name, rtttl: rtttl, id: String(id) };

    addSong(newSong);
    client.publish(mod_topic, JSON.stringify(songs), {qos: 0, retain: false}, (error) => {
        if (error) {
            console.error(error);
        }
    })
    res.redirect('/commands');

});

app.delete('/:id', async (req, res) => {
    for (let i = 0; i < songs.length; ++i) {
        if (String(songs[i].id) === req.params.id) {
            songs.splice(i, 1);
            fs.writeFile("songs.json", JSON.stringify(songs), (err) => {
                if (err) {}

            });

            client.publish(mod_topic, JSON.stringify(songs), {qos: 0, retain: false}, (error) => {
                if (error) {
                    console.error(error);
                }
            })
            res.statusCode = 200 ;
            return res.end();
        }
    }



    res.statusCode = 401;
    return res.end();
});

server.listen(PORT);


const addUser = (newUser) => {
    return new Promise((resolve, reject) => {
        MongoClient.connect(mongo_url, function (err, db) {
            if (err) reject("FAILED TO CONNECT TO DATABASE");
            const dbo = db.db("users");

            dbo.collection("users").find({username: newUser.username}).toArray((err, res) => {
                if (res[0] !== undefined) reject("USERNAME ALREADY TAKEN");
                else {
                    dbo.collection("users").insertOne(newUser, function (err) {
                        if (err) reject("FAILED TO ADD NEW USER TO DATABASE. PLEASE TRY AGAIN.");
                        resolve("SIGNED UP SUCCESSFULLY");
                        db.close();
                    });
                }
            });
        });
    });
}





