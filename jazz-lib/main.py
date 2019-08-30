"""
    Command line tool that lets users search and discover jazz albums from Discogs.

"""
from collections import Counter
from discogs_cli.discogs import Release
from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import CompleteStyle, prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.document import Document
import discogs_client
import pprint
import pymongo
import spotipy
import spotipy.util as util
import webbrowser

class noMetaCompleter(Completer):
    """
        Autocomplete with no meta info.

        Params: (p_array) values of album attribute (year, country, labels, or artist), sorted by rank
                (p_dict)  key -- album attribute, value -- count

    """
    def __init__(self, p_array, p_dict):
        self.array = p_array
        self.dict = p_dict

    def get_completions(self, document, complete_event):
        param_array = self.array
        param_dict = self.dict
        
        family_colors = {}
        meta = {}

        word = document.get_word_before_cursor()
        for param in param_array:
            if param.startswith(word):
                if param in param_dict:
                    family = param_dict[param]
                    family_color = family_colors.get(family, 'default')

                    display = HTML(
                        '%s<b>:</b> <ansired>(<' + family_color + '>%s</' + family_color + '>)</ansired>'
                        ) % (param, family)
                else:
                    display = param

                yield Completion(
                    param,
                    start_position=-len(word),
                    display=display,
                    display_meta=meta.get(param)
                )

class metaCompleter(Completer):
    """
        Autocomplete with meta info (year, label, and country).
        
        Params: (p_array) array values of album attribute (album), sorted by year
                (p_dict)  dictionary containing key -- album title, value -- artist
                (p_meta)  dictionary containing meta data

    """
    def __init__(self, p_array, p_dict, p_meta):
        self.array = p_array
        self.dict = p_dict
        self.meta = p_meta

    def get_completions(self, document, complete_event):
        param_array = self.array
        param_dict = self.dict

        
        family_colors = {}
        meta = self.meta
        out = ''

        word = document.get_word_before_cursor()
        for param in param_array:
            if param.startswith(word):
                if param in param_dict:
                    family = param_dict[param]
                    family_color = family_colors.get(family, 'default')
                    out = family[family.find("_"):family.find("*")]
                    display = HTML(
                        '%s<b>:</b> <ansired>(<' + family_color + '>%s</' + family_color + '>)</ansired>'
                        ) % (param, family[family.find("*")+1:])
                else:
                    display = param

                yield Completion(
                    param,
                    start_position=-len(word),
                    display=display,
                    display_meta=meta.get(param),

                )
        document = document.insert_before(out)
            # print("this is meta.get(param):  "+str(meta.get(param)))
            # print("this is display: "+str(display))

def main():
    """
        Command line app that lets users discover Discogs'jazz albums by querying album JSON data from Mongo
        Query order: year > country > label > artist > album

    """
    years_obj = getDictYears()
    d = discogs_client.Client('jazz-personnel/0.1')
    while True:

        """
            Year query

        """
        year = prompt('Enter year range or year: ', completer=noMetaCompleter(years_obj["year_array"], years_obj["year_dict"]),complete_style=CompleteStyle.MULTI_COLUMN)
        year = prettyArray(year)

        """
            Country query

        """
        country = prompt('Enter country range or country: ', completer=getCountryCompleter(years_obj["year_dict"],year),complete_style=CompleteStyle.MULTI_COLUMN, default="("+str(year)+") ")
        country = prettyArray(country[country.find(")")+2:])
       
        """
            Label query

        """
        label = prompt('Enter a label: ' , completer=getLabelCompleter(year,country),complete_style=CompleteStyle.MULTI_COLUMN, default="("+str(year)+" > "+str(country)+") ")
        label = prettyArray(label[label.find(")")+2:])

        """
            Artist query

        """
        artist = prompt('Enter an artist: ', completer=getArtistCompleter(year,country,label),complete_style=CompleteStyle.MULTI_COLUMN)
        artist = prettyArray(artist[artist.find(")")+1:])

        """
            Album query. Returns Discogs release data through discogs-cli

        """
        album_obj = getAlbumCompleter(year,country,label,artist)
        more = 'a'
        while more == 'a':
            album = prompt('Enter an album: ', completer=metaCompleter(album_obj["name"], album_obj["dict"],album_obj["meta"]),complete_style=CompleteStyle.COLUMN)
            results = Release(album_obj["id"][album], include="personnel")
            results.show()
            more = input("Press [ENTER] for new search. Input ['a'] to query another album, ['s'] to search Spotify: ")
            while more == 's':
                """
                    Command line input for credentials:
                        export SPOTIPY_CLIENT_ID='f4dfbd09f8e74c22aba3ad3adb120b7f'
                        export SPOTIPY_CLIENT_SECRET='4436e38ff04e4aecbf137aec581b0a77'
                        export SPOTIPY_REDIRECT_URI='https://verve3349.wordpress.com/'

                """
                token = util.prompt_for_user_token('125088194')
                sp = spotipy.Spotify(auth=token)
                result = sp.search(str(artist), type='artist')
                artist_id = ''
                try:
                    artist_id = result["artists"]["items"][0]["id"]
                    artist_albums = sp.artist_albums(artist_id, album_type='album',limit=50)
                    url = 'Does not exist in Spotify'
                    for each in artist_albums['items']:
                        if album in each["name"]:
                            url = each['external_urls']['spotify']
                    print(url)
                    webbrowser.open(url)
                except:
                    print("Try manual search.")
                more = input("Press [ENTER] for new search. Input ['a'] to query another album: ")
def getDictYears():
    """
        Retrieve all years of Discogs jazz release data

        Returns: (yearObj) object containing
            (year_array)  array of years
            (year_dict)   dictionary of year occurences

    """
    client = pymongo.MongoClient("localhost", 27017)
    db = client.final_jazz_releases
    albums = db.current.find({},{"releases.release.released":1})
    all_years = {}
    for album in albums:
        try:
            a_year = album["releases"]["release"]["released"]
            a_year = a_year[:4]
            year = a_year
            decade = year[:3]+"0s"
            if year in all_years:
                all_years[year] += 1
            else:
                all_years[year] = 1
            if decade in all_years:
                all_years[decade] += 1
            else:
                all_years[decade] = 1
        except:
            n=0
    sorted_x = sorted(all_years.items(), key=lambda kv: kv[1])
    new_arr = []
    for i in range(0,100):
        new_arr.append(sorted_x[len(sorted_x)-1-int(i)])
    year_list = []
    new_years = {}
    for each in new_arr:
        year_list.append(str(each[0]))
        new_years[str(each[0])] = str(each[1])
    yearsObj = {
        "year_array": year_list,
        "year_dict": new_years
    }
    return yearsObj

def getCountryCompleter(dict_years, year):
    """
        Retrieve all countries of Discogs jazz release data within selected year
        
        Params: (dict_years)  dictionary of year occurences
                (year)        array containing selected year(s)

        Returns: (noMetaCompleter) object containing
            (countries)      array of countries
            (new_countries)  dictionary of country occurences

    """
    client = pymongo.MongoClient("localhost", 27017)
    db = client.final_jazz_releases
    year = decadeCheck(year)
    albums = db.current.find({"releases.release.released": {"$in": year}},{"releases.release.country":1})
    countries_dict = {}
    for album in albums:
        try:
            country = album["releases"]["release"]["country"]
            if country not in countries_dict:
                countries_dict[country]=1
            else:
                countries_dict[country]+=1
        except:
            n=0
    countries_dict = sorted(countries_dict.items(), key=lambda x: x[1], reverse=False)
    new_arr = []
    for i in range(0,len(countries_dict)):
        new_arr.append(countries_dict[len(countries_dict)-1-int(i)])
    countries = []
    new_countries = {}
    for each in new_arr:
        countries.append(each[0])
        new_countries[each[0]] = each[1]
    return noMetaCompleter(countries, new_countries)

def getLabelCompleter(year, country):
    """
        Retrieve all labels of Discogs jazz release data within selected year and country
        
        Params: (year)      array containing selected year(s)
                (country)   array containing selected country(s)

        Returns: (noMetaCompleter) object containing
            (names)      array of label
            (new_labels) dictionary of label occurences

    """
    client = pymongo.MongoClient("localhost", 27017)
    db = client.final_jazz_releases
    year = decadeCheck(year)
    albums = db.current.find({"releases.release.released": {"$in": year},"releases.release.country":{"$in":country}},{"releases.release.labels.label.@name" :1})
    labels_dict = {}
    for album in albums:
        album = album["releases"]["release"]["labels"]["label"]
        try:
            name = album.get("@name")
        except:
            name = album[0].get("@name")
        if name not in labels_dict:
            labels_dict[name]=1
        else:
            labels_dict[name]+=1
    labels_dict = sorted(labels_dict.items(), key=lambda x: x[1], reverse=False)
    new_arr = []
    for i in range(0,len(labels_dict)):
        new_arr.append(labels_dict[len(labels_dict)-1-int(i)])
    names = []
    new_labels = {}
    for each in new_arr:
        names.append(each[0])
        new_labels[each[0]] = each[1]
    return noMetaCompleter(names, new_labels)

def getArtistCompleter(year, country, label):
    """
        Retrieve all artists of Discogs jazz release data within selected year, country, and label
        
        Params: (year)      array containing selected year(s)
                (country)   array containing selected country(s)
                (label)     array containing selected label(s)

        Returns: (noMetaCompleter) object containing
            (artist_names)      array of artists
            (new_artists_dict)  dictionary of artist occurences

    """
    client = pymongo.MongoClient("localhost", 27017)
    db = client.final_jazz_releases
    year = decadeCheck(year)
    albums = db.current.find({"releases.release.released": {"$in": year},"releases.release.country":{"$in": country},"releases.release.labels.label.@name": {"$in": label}},{"releases.release.artists.artist.name" :1})
    artists_dict = {}
    for album in albums:
        name = ''
        try:
            name = album["releases"]["release"]["artists"]["artist"]["name"]
        except:
            name = album["releases"]["release"]["artists"]["artist"][0]["name"]
        if name not in artists_dict:
            artists_dict[name]=1
        else:
            artists_dict[name]+=1
    artists_dict = sorted(artists_dict.items(), key=lambda x: x[1], reverse=False)
    new_arr = []
    for i in range(0,len(artists_dict)):
        new_arr.append(artists_dict[len(artists_dict)-1-int(i)])
    artist_names = []
    new_artists_dict = {}
    for each in new_arr:
        artist_names.append(each[0])
        new_artists_dict[each[0]] = each[1]
    return noMetaCompleter(artist_names, new_artists_dict)

def getAlbumCompleter(year, country, label, artist):
    """
        Retrieve all albums of Discogs jazz release data within selected year, country, label, and artist
        
        Params: (year)      array containing selected year(s)
                (country)   array containing selected country(s)
                (label)     array containing selected label(s)
                (artist)    array containing selected artist(s)


        Returns: (metaCompleter) object containing
            (album_names)     array of artists
            (new_album_dict)  dictionary of artist occurences
            (meta_dict)       dictionary of meta information (year, label, country)
    """
    client = pymongo.MongoClient("localhost", 27017)
    db = client.final_jazz_releases
    year = decadeCheck(year)
    albums = db.current.find({"releases.release.released": {"$in": year},"releases.release.country":{"$in": country},"releases.release.labels.label.@name": {"$in": label}},{"releases.release.@id":1,"releases.release.artists":1,"releases.release.title":1,"releases.release.released":1,"releases.release.country":1, "releases.release.labels.label":1})
    albums_dict = {}
    meta_dict = {}
    year_meta = {}
    album_id_dict = {}
    for album in albums:
        album_id =  album["releases"]["release"]["@id"]
        # album_id = album_id.get("@id")
        label_name = ''
        label = album["releases"]["release"]["labels"]["label"]
        try:
            label_name = label.get("@name")
        except:
            label_name = label[0].get("@name")

        current_country = album["releases"]["release"]["country"]
        current_year = album["releases"]["release"]["released"][:4]
        title = album["releases"]["release"]["title"]
        name = ''
        try:
            name = album["releases"]["release"]["artists"]["artist"]["name"]
        except:
            name = album["releases"]["release"]["artists"]["artist"][0]["name"]
        if name in artist:
            albums_dict[title]=current_year+"_"+album_id+"*"+name
            meta_dict[title] = HTML(current_year+" ["+label_name+", "+current_country+"]")
            year_meta[title] = current_year
        album_id_dict[title] = album_id
    albums_dict = sorted(albums_dict.items(), key=lambda x: x[1], reverse=False)
    year_meta = sorted(year_meta.items(), key=lambda x: x[1], reverse=False)
    new_arr = []
    year_arr = []
    for i in range(0,len(albums_dict)):
        new_arr.append(albums_dict[len(albums_dict)-1-int(i)])
        year_arr.append(year_meta[len(year_meta)-1-int(i)])
    album_names = []
    new_album_dict = {}
    new_meta_dict = {}
    for each in new_arr:
        # print(each)
        album_names.append(each[0])
        new_album_dict[each[0]] = each[1]
    albumObj = {
        "name": album_names,
        "dict": new_album_dict,
        "meta": meta_dict,
        "id": album_id_dict
    }
    return albumObj
    return metaCompleter(album_names, new_album_dict,meta_dict)

def prettyArray(param):
    """
        Converts prompt inputs from string to array. Puts multiple arguments in a single array

        Param: (param) prompt input string (year, country, label, or artist inputs)

        Returns: (param.split(", ")) prompt input as an array

    """
    if "," in param and " " not in param:
        param = param.replace(",",", ")
    return param.split(", ")

def decadeCheck(year):
    """
        Converts year decade input into an array of decade's years

        Param: (year) string of the decade e.g. '1970s'

        Returns: (year_query) array of decade's years

    """
    year_query= []
    if "s" in year[0]:
        start = year[:4]
        for i in range(0,10):
            # print(str(year[0][:3])+str(i))
            year_query.append(str(year[0][:3])+str(i))
    else:
        year_query = year
    return year_query

if __name__ == '__main__':
    main()