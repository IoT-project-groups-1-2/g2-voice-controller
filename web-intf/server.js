'use strict'

//Getting node modules
const express = require('express');
const app = express();
const path = require('path');
const mqtt = require('mqtt');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const {hashPassword, verifyPassword} = require("./pbkdf2");
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const MongoClient = require('mongodb').MongoClient;





app.use(bodyParser.urlencoded({extended: true}));
app.use(cookieParser());

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

//Defining constants
const PORT = process.env.PORT || 3000;
const broker_url = 'mqtt://127.0.0.1:1883';
const mongo_url = 'mongodb://localhost:27017';
const client = mqtt.connect(broker_url, { clientId: 'node', clean: true });
const settings_topic = "controller/settings";
const status_topic = "controller/status";

client.on('connect', ()=>{
    console.log('MQTT client connected: '+ client.connected);
});
client.subscribe(status_topic, () => {
    console.log("subscribed to " + status_topic);
});

client.subscribe(settings_topic, () => {
    console.log("subscribed to " + settings_topic);
});

io.on('connection', (socket)=> {
    console.log("User " + socket.id + " connected");
    client.on('message', (topic, msg) => {
        client.removeAllListeners();
        msg = msg.toString();
        io.emit('settings',msg);
        console.log(msg+ " sent through websocket");
    })

});

io.on('connection', (socket)=> {
    socket.on("datas",(arg)=>{
            client.publish(settings_topic, arg, {qos: 0, retain: false}, (error) => {
                console.log(arg + " published to:" + settings_topic);
                if (error) {
                    console.error(error);
                }
            })
    })
});


//S
io.on('connection', (socket)=> {
    console.log("User " + socket.id + " connected");
    MongoClient.connect(mongo_url, function (err, db) {
        if (err) reject("FAILED TO CONNECT TO DATABASE");
        const dbo = db.db("songs");

        dbo.collection("songs").find({}).project( {Name:1,_id:0}).toArray( (err, res) => {
            io.emit('songList',res);
        });

    })

});

//Send a particular song to MQTT
io.on('connection', (socket)=> {
    socket.on("songs",(arg)=>{
        client.publish(settings_topic, arg, {qos: 0, retain: false}, (error) => {
            console.log(arg + " published to:" + settings_topic);
            if (error) {
                console.error(error);
            }
        })
    })
});

// app.get('/voice-data',(req, res) => {
//
//     client.on('message', (topic, msg) => {
//         client.removeAllListeners();
//         msg = msg.toString();
//         console.log(msg);
//         return res.json(msg);
//     });
//     // res.send("yolo");
//
// });


app.get('/', async (req, res) => {
    res.render("login");
});

app.get('/signup', (req, res) => {
    if(req.cookies.loggedIn === "true") return res.redirect('/home');
    res.render('signup');
});

app.get('/home', (req, res) => {
    if(req.cookies.loggedIn === "false") return res.redirect('/');
    res.render('home');
});

//logout route and redirects to the login page
app.get('/logout', (req, res) => {
    if(req.cookies.loggedIn === "true") {
        res.cookie("curr_user", "");
        res.cookie("loggedIn", false);
    }
    res.redirect('/home');
});
app.get('/commands',(req, res)=>{
    if(req.cookies.loggedIn === "false") return res.redirect('/');
    res.render('command');

})

// app.get('/api/songs',(req, res) => {
//     let test = [];
//     MongoClient.connect(mongo_url, function (err, db) {
//         if (err) reject("FAILED TO CONNECT TO DATABASE");
//         const dbo = db.db("songs");
//
//         dbo.collection("songs").find({}).project( {Name:1,_id:0}).toArray( (err, res) => {
//         });
//
//     })
//     res.json(res);
// });
//

// app.get('/api/songs',(req, res) => {
//
//
//     MongoClient.connect(mongo_url, function (err, db) {
//         const dbo = db.db("songs");
//         dbo.collection("songs").insertMany(songs, function (err) {
//             if (err) reject("FAILED TO ADD NEW USER TO DATABASE. PLEASE TRY AGAIN.");
//             db.close().then(r => console.log(r));
//         });
//     });
// });
app.post('/signup', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    hashPassword(password).then(hashedPassword => {
        const newUser = {username, hashedPassword};
        addUser(newUser).
        then(msg => {
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


app.post('/login', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    let query_obj = { username: username };
    MongoClient.connect(mongo_url, function(err, db) {
        if (err) throw err;
        const dbo = db.db("users");
        dbo.collection("users").find(query_obj).toArray((err, user_arr) => {
            const user = user_arr[0];
            if(user !== undefined) {
                //checking if the inputted password matches the password from the database
                verifyPassword(password, user.hashedPassword)
                    .then((equal) => {

                        if(equal) {
                            res.statusCode = 200;
                            if(req.cookies.curr_user !== user.username) {
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
                console.log("USERNAME NOT FOUND");
                res.cookie("login_err", 401);
                return res.redirect('/');
            }
        });
    });
});

server.listen(PORT);


const addUser = (newUser) => {
    return new Promise((resolve, reject) => {
        MongoClient.connect(mongo_url, function (err, db) {
            if (err) reject("FAILED TO CONNECT TO DATABASE");
            const dbo = db.db("users");

            dbo.collection("users").find({username: newUser.username}).toArray( (err, res) => {
                if(res[0] !== undefined) reject("USERNAME ALREADY TAKEN");
                else {
                    dbo.collection("users").insertOne(newUser, function (err) {
                        if (err) reject("FAILED TO ADD NEW USER TO DATABASE. PLEASE TRY AGAIN.");
                        resolve("SIGNED UP SUCCESSFULLY");
                        db.close().then(r => console.log(r));
                    });
                }
            });
        });
    });
}





