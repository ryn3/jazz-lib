# jazz-lib

This app acts as a library search tool for Discogs' jazz records. Search by decade(s)/year(s), country(s), label(s), and then artist(s)  

Download MongoDB if needed from <https://www.mongodb.com/download-center/community>

## Specifications
The Mongo database uses localhost: 27017

* Database name: **discogs_masters** 

* Collections: **current_albums** (saved Spotify albums) **current_masters** (Discogs masters). 

## Dependencies

	$ pip install -r requirements.txt

## Usage

### 1. Import jazz release data to Mongo
	
	$ cd jazz-lib
	$ chmod +x import_discogs_masters.sh
	$ ./import_discogs_masters.sh

### 2. Run jazz-lib
	
	$ python3 main.py

#### Example: 

	Enter year range or year: 1960s
	Enter country range or country: (['1960s']) US
	Enter a label: (['1960s'] > ['US']) Columbia
	Enter an artist: Thelonious Monk
	Enter an album: Criss-Cross
	Thelonious Monk [145256] - Criss-Cross
	Label:    Columbia (CL 2038) [1866]
	Format:   Vinyl (LP, Album, Mono)
	Country:  US
	Year:     1963
	Genre:    Jazz
	Style:    Post Bop
	Rating:   4.49/5
 	-- [ Personnel ] ----------------------------------
	Bass:  John Ore
	Drums:  Frankie Dunlop
	Liner Notes:  Nica De Koenigswarter
	Photography By:  Sandy Speiser
	Piano:  Thelonious Monk
	Producer:  Teo Macero
	Tenor Saxophone:  Charlie Rouse

## About

This app was inspired in part by:
* python-prompt-toolkit by Jonathan Slenders <https://github.com/prompt-toolkit/python-prompt-toolkit>
* discogs-cli by Jesse Ward <https://github.com/jesseward/discogs-cli>
* spotipy by Paul Lamere <https://github.com/plamere/spotipy>
