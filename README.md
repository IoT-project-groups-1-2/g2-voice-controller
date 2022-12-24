# g2-voice-controller

## Description
This project is about digital audio, whereas a RTTTL string will be sent by the web side, using voice recognition to the Raspberry Pico through MQTT, and the string will parse into playable audio and played through the piezzo-buzzer. 


## User Manual

- #### Operation:
	User is free to operate this system from both the hardware side and the web side, whereas users can play the song which is saved as a RTTTL string format. 
	- #### Physcial user interface: 
	When the whole system is turned on, Raspberry Pico will try to connect to the internet via WIFI. LCD will display a loading screen when WIFI is not connect, after connecting to WIFI, there are three buttons to navigate the on-screen list of songs. The top line displays the currently selected song on the list. Left and right buttons move up and down the list of songs (buttons <- | ->), while the center button selects the currently selected song for playback. When Raspberry Pico received a RTTTL string through MQTT from the web, it will temporary disable the menu, and only displays the song name that it received. After a RTTTL string is received, Rasspberry Pico will parse the string. Musical note in RTTTL format is a tuple containing the note duration and note key, or frequency. The notes are iterated through and each note is referenced to a lookup table that contains their frequency at the base octave, that is then multiplied to match the desired note frequency. Likewise the note duration is altered from the default if a modifier is present on the note. The parsed data contains two values, note length in ms and frequency in Hz, that are output into a table for the main program to output to a buzzer as PWM signal.
	- #### Web UI interface:
	The web UI requires user authentication to access, allowing the creation of new user profiles at will. While logged in on a profile, the home page displays options to record microphone input for a voice command, also displaying the name of the current user. Moreover, users can access the whole playlist of the songs and they are free to add a song in RTTTL format. To play a song, users need to press the microphone button at the bottom left hand side of the web page and a command **Play Song *Song Number*** is needed in order to let the piezo-buzzer play the song. In addition, there is a **10 second countdown timer** in the middle of the web page, indicating the remaining time to speak. If the web does not recognize any command in the 10 second period, it will stop listening and users need to press the microphone icon again. When the **view songlist** button is pressed, users will be directed into a page whereas the whole songlist will be displayed. Users can read through the list and choose a song number. Moreover, the list is clickable so that if an item is pressed, it can also serve the same function as using the microphone. Lastly, the bin icon will allow users to delete a song that they do not like. When the  **Add a song** button is pressed, it will redirect to a page where user can add a song by its song name, and its RTTTL string respectively. The RTTTL string format is restricted so that if the user inputed an incorrect format, a warning will pop out. 

- #### Back-End
	1. ###### Server
		The language choice for backend server was NodeJs along with Express. The server was implemented with simplicity in mind, so it only contains most basic routes for login, signup, logout, posting data and sending views. The authentication system used **PBKDF2** for password encryption. The server has access to cookies and it takes part in managing the state of the website.
	2. ###### Database
		MongoDB was the go to option for this project due to ease of use and its compability with NodeJs and its popularity among the web devs community. The app uses 1 collection, **users**. Users collection, obviously contain user credentials.User's ID can be implemented but with Mongo DB's built-in auto ID assignment it is not necessary for now.
	3. ###### SongList
   Songs that the server has access to are stored in a .json database file, whereas every object contains the song name, the RTTTL string and also the ID of the song.
   ## Developement Process
   The development started with a concept for a device to issue voice commands to a moving robot. This device would’ve, in theory, record PCM stream from an I2S MEMS microphone and parse commands with a software implementation running natively on the board itself. The board we were planning to use was BeagleBone Black, with plenty of processing headroom and memory for functional voice recognition libraries (such as tensorflow). We sourced components for the I2S MEMS microphone, I2S 3W amplifier and speaker elements. However, advancing from this initial concept was marred with issues including library management, problems affecting internet connectivity via USB, and poor utilisation of the existing software development pipelines for the board. As a
result progress was too slow to ever see the project come to fruition by the deadline.

	Second revision of the project removed the BeagleBone Black in favor of Raspberry Pi Pico running Micropython. This gave the needed acceleration and support to produce a functioning project on time. However, we were still attempting to utilise the sourced I2S MEMS microphone, I2S 3W amplifier and dedicated speaker element for a high quality audio capture and playback. While we managed to get data from the microphone, the file management in persistent flash memory on the Raspberry Pi Pico proved challenging, and as we had lost time already on the previous iteration of the project, we were forced to further simplify the design. 
	
	In addition to problems with the microphone, we were unable to get the I2S amplifier to
output any analog signal from the output terminals. This forced us to completely
abandon the original design, and instead focus on a simpler implementation using voice
recording on a separate computer and audio output via previously outlined PWM output
on a piezo-buzzer.


## Contributors

[Kendrick Kwong](https://github.com/kendrick-807)

[Long Pham](https://github.com/phamduylong)

[Jaakko Nahkala](https://github.com/jaakkoiot)

