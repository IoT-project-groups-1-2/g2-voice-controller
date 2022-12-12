const songs = require('./songs.json');
const fs = require("fs");
 const addSong = (rtttl_obj) => {
     songs.push(rtttl_obj);
     fs.writeFile("songs.json", JSON.stringify(songs), (err) => {
         if (err)
             console.log(err);
     });


}

exports.playlist = songs
exports.addSong = addSong