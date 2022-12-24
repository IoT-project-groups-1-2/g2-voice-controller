# g2-voice-controller

## Description
This project is about digital audio, whereas an RTTTL string will be sent by the website using voice recognition to the Raspberry Pico through MQTT, or chosen from the LCD interface and the string will be parsed into playable audio and played through the piezo-buzzer. 


## User Manual

- ### Operation:
	User is free to operate this system from both the hardware side and the web side, whereas users can play the song which is saved as an RTTTL string. During the duration of a song, the connected LED will be toggled, indicating of a song being played.
	- #### Physical User Interface: 
	When the whole system is turned on, Raspberry Pi Pico W will try to connect to the internet via Wifi, after which it will use to fetch the song database from the website. There are three buttons to navigate the on-screen list of songs. The top line displays the currently selected song on the list. The Left and right buttons move up and down the list of songs (buttons <- | ->), while the center button selects the currently selected song for playback. When the device received an RTTTL string through MQTT from the web, it will temporarily disable the menu, and only displays the song name that it received, parse the string and play it. A musical note in RTTTL format is a tuple containing the note duration and note key, or frequency. The notes are iterated through and each note is referenced to a lookup table that contains their frequency at the base octave, which is then multiplied to match the desired note frequency. Likewise, the note duration is altered from the default if a modifier is present on the note. The parsed data contains two values, note length in ms and frequency in Hz, that are output into a table for the main program to output to a buzzer as PWM signal.
	- #### Web Interface:
	The Web UI requires user authentication to access, allowing the creation of new user profiles at will. While logged in on a profile, the home page displays options to record microphone input for a voice command, also displaying the name of the current user. Moreover, users can access the whole playlist of songs and they are free to add a song in RTTTL format. To play a song, users need to press the microphone button at the bottom left-hand side of the web page and a command:
	 >**Play song [number]** 
	 
	 In addition, there is a **10-second countdown timer** in the middle of the web page, indicating the remaining time to speak. If the web does not recognize any command within 10 seconds, it will stop recording and the user need to press the microphone icon again. When the **View Song list** button is pressed, users will be directed to a page where the whole song list will be displayed. Users can read through the list and choose a song number. Moreover, the list is clickable so that if an item is pressed, it can also serve the same function as using the microphone. Lastly, the bin icon will allow users to delete a song that they do not like. Pressing the **Add a song** will redirect to a page where the user can add a song by its song name, and its RTTTL string respectively. The RTTTL string format is restricted so that if the user inputs an incorrect format, a warning will pop up. 

## Technical Information
- ### Embedded Devices
	- #### MicroController
		Raspberry Pi Pico W was the choice for the project. It is a powerful, easy to use board with built-in Wifi support, decent clock speed and a great amount of RAM.
	
	- #### Piezo Buzzer
		We used a normal piezo buzzer in order to cutoff complexity. The buzzer is driven with 50% duty cycle.
	
	 
- ### Back-End
	- #### Server
		The language choice for the backend server was NodeJs along with Express. The server was implemented with simplicity in mind, so it only contains the most basic routes for login, signup, logout, posting data, and sending views. The authentication system used **PBKDF2** for password encryption. The server has access to cookies and it takes part in managing the state of the website.
	- #### Database
		MongoDB was the go-to option for this project due to its ease of use and its compatibility with NodeJs and its popularity among the web devs community. The app uses 1 collection, **users**. Users collection, obviously contain user credentials. User's ID can be implemented but with Mongo DB's built-in auto ID assignment it is not necessary for now.
	- #### SongList
   		Songs that the server has access to are stored in a .json file, whereas every object contains the song name, the RTTTL string, and also the ID of the song.



## Contributors

[Kendrick Kwong](https://github.com/kendrick-807)

[Long Pham](https://github.com/phamduylong)

[Jaakko Nahkala](https://github.com/jaakkoiot)

