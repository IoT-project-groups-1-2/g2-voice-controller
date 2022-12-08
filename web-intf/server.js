'use strict'

//Getting node modules
const express = require('express');
const path = require('path');
const mqtt = require('mqtt');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const {hashPassword, verifyPassword} = require("./pbkdf2");
const MongoClient = require('mongodb').MongoClient;

const app = express();


app.use(bodyParser.urlencoded({extended: true}));
app.use(cookieParser());

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

//Defining constants
const PORT = process.env.PORT || 3000;
const broker_url = 'mqtt://127.0.0.1:1883';
const mongo_url = '';
const client = mqtt.connect(broker_url, { clientId: 'node', clean: true });
const settings_topic = "controller/settings";
const status_topic = "controller/status";



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
app.get('/voice-data',(req, res) => {

    client.on('message', (topic, msg) => {
        client.removeAllListeners();
        msg = msg.toString();
        console.log(msg);
        return res.json(msg);
    });
    // res.send("yolo");

});

//logout route and redirects to the login page
app.get('/logout', (req, res) => {
    if(req.cookies.loggedIn === "false") return res.redirect('/');
    const username = req.cookies.curr_user;
    MongoClient.connect(mongo_url, function (err, db) {
        if (err) console.error("FAILED TO CONNECT TO DATABASE");
        const dbo = db.db("users");
        dbo.collection("users").find({username: username}).toArray((err, arr) => {
            if (err) throw err;
            if(arr[0] !== undefined) {
                const user = arr[0];
                    dbo.collection("users").updateOne({username: username}).then((res) => {
                        console.log(res);
                    })
                }
            });
        });


    res.cookie("curr_user", "");
    res.cookie("loggedIn", false);
    res.redirect('/');
});


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
                                dbo.collection("users").updateOne({username: user.username},
                                    (err, res) =>{
                                        if(err) throw err;
                                        console.log(res);
                                    });
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

app.listen(PORT);


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







