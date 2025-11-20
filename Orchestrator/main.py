import music_tag
from PIL import Image
import math
import time
import os
import shutil
import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed

NEEDED_TAGS = ["title","artist","album","albumartist","genre","totaltracks","tracknumber","year"]
WARN_TITLE_STRINGS = [" remaster "," remastered ", " feat ", " featuring ", "feat. "]
WARN_ARTIST_STRINGS = [" x "," with ", " feat ", " & ", " featuring ", " feat. "," + ", ","]
WARN_ALBUMARTIST_STRINGS = WARN_ARTIST_STRINGS + [";"]
WARN_ALBUM_STRINGS = [" greatest ", " hits ", " best of "]
ACCEPTED_GENRES = ["Rock", "Pop Rock", "Arena Rock", "Glam Metal", "Metal", "Pop", "Soundtrack", "Movie Soundtrack", "Synth", "Synth Pop", "Dance", "Vocaloid", "Electronic", "Japan", "House", "Ballad", "Adult Alternative", "Adult Contemporary", "Piano", "R&B", "Dance Pop", "Synth Funk", "Hip-Hop", "Funk", "Swing", "Electro Swing", "Hardcore", "Instrumental", "New Wave", "Synth Rock", "J-Pop", "Anime", "J-Rock", "Soul", "Rap", "West Coast Rap", "Techno", "Experimental", "Future Bass", "Electro House", "Soft Rock", "Singer Songwriter", "Remix", "Video Game Music", "Alternative Pop", "Trap", "Trip-Hop", "South Korea", "Nerdcore", "K-Pop", "Reggae", "Dubstep", "Classical", "Orchestral", "Alternative Rock", "Alternative", "Nightcore", "Cover", "Storytelling", "Country", "Country Rock", "Hardcore Rap", "Gangsta Rap", "Political", "Protest Songs", "Punk", "Folk", "Indie Rock", "Album Oriented Rock", "Hard Rock", "Psychedelic Rock", "Blues Rock", "EDM", "Electro Pop", "Glam Rock", "Complextro", "Indie", "J-Metal", "Futurecore", "Dark Pop", "Ambient", "Progressive House", "Diss", "Heavy Metal", "Happy Hardcore", "Thrash Metal", "Future House", "Blues", "Disco", "Jazz", "Drum & Bass", "Bass", "Psychedelic Soul", "Progressive Soul", "Progressive Rock", "Memes", "Rock & Roll", "Alternative Hip-Hop", "Conscious Hip-Hop", "Glitch-Hop", "Alternative Metal", "Chill", "Classic Rock", "Glitch", "Psychedelic Pop", "Latin", "Drumstep", "Indie Folk", "Indie Pop", "Progressive Metal", "Hyper Pop", "Future Pop", "Breakcore", "Experimental Rock", "Brostep", "Traditional Pop", "Comedy", "Parody", "Hybrid Trap", "Vocal", "Russia", "Indie Dance", "Smooth Jazz", "Chiptune", "Trance", "Speedcore", "Horrorcore", "Korea", "Contemporary R&B", "Bass House", "Speed Metal", "West Coast Hip-Hop", "Hardcore Hip-Hop", "Southern Rock", "Power Metal", "Country Pop", "Psychedelic", "Teen Pop", "East Coast Rap", "Electornic", "Symphonic Metal", "Symphonic Rock", "Melodic", "Gangsta Hip-Hop", "Experimental Hip-Hop", "Hardstyle", "Gospel", "Comedy Hip-Hop", "Dance Rock", "Sea Shanty", "Freestyle", "Folk Rock", "Future Trap", "Alternative R&B", "Alternative Dance", "Eurobeat", "India", "Alternative Rap", "Southern Hip-Hop", "Alternative Country", "Micropop", "Future Funk", "Acoustic", "Propaganda", "Progressive Pop", "Death Metal", "Southern Rap", "K-Indie", "K-Rock", "Progressive Rap", "Conscious Rap", "East Coast Hip-Hop", "Traditional", "Western", "Opera", "Progressive Hip-Hop", "Psytrance"]
FILESYSTEM_INVALID_CHARS = ["\\","/",":","*","?","\"","<",">","|"]

FILESYSTEM_PATH = os.getenv("FILESYSTEM_PATH")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def make_safe(string):
    for char in FILESYSTEM_INVALID_CHARS:
        string = string.replace(char,"")
    return string

def check_main_tag(value, checkList):
    if value:
        for string in checkList:
            if string in value.lower():
                # if tag contains warning strings
                return "🟡"
        return "🟢"
    else:
        # if tag is empty
        return "🔴"

def check_genre(genres):
    if genres:
        genre_list = genres.split(";")
        for genre in genre_list:
            if not genre.strip() in ACCEPTED_GENRES:
                return "🟡"
        return "🟢"
    else:
        return "🔴"

def fix_genres(audioFile):
    if audioFile["genre"]:
        genre_list = str(audioFile["genre"]).split(";")
        fixed_genre_list = []
        for genre in genre_list:
            if genre.strip() in ACCEPTED_GENRES:
                fixed_genre_list.append(genre.strip())
        if fixed_genre_list != []:
            audioFile["genre"] = "; ".join(fixed_genre_list)
            return True
        else:
            audioFile["genre"] = ""
            return False
    else:
        return False

def check_number_tag(value, min, max):
    if value and max:
        try:
            intVal = int(value)
            intMax = int(max)
            if intVal >= min and intVal <= intMax:
                return "🟢"
            else:
                return "🔴"
        except:
            return "🔴"
    else:
        return "🔴"

def get_artwork_size(audioFile):
    try:
        with open('artwork.png', 'wb') as artworkImg:
            artworkImg.write(audioFile["artwork"].first.data)
        img = Image.open('artwork.png')
        size = str(img.width)+" x "+str(img.height)
        img.close()
        return size
    except:
        return "0 x 0"

def fix_artwork(audioFile):
    try:
        with open('artwork.png', 'wb') as artworkImg:
            artworkImg.write(audioFile["artwork"].first.data)
        img = Image.open('artwork.png')
        if img.width != img.height:
            startx = 0
            starty = 0
            image_res = str(img.width)+" x "+str(img.height)
            if img.width > img.height:
                startx = math.floor((img.width-img.height)/2)
                size = img.height
            elif img.height > img.width:
                starty = math.floor((img.height-img.width)/2)
                size = img.width

            cropped_img = img.crop((startx, starty, startx+size, starty+size))
            cropped_img.save('artwork.png')
            with open('artwork.png', 'rb') as fixed_art:
                audioFile["artwork"] = fixed_art.read()
        return True
    except:
        return False

def check_artwork(audioFile):
    try:
        size = get_artwork_size(audioFile)
        width = size.replace(" ","").split("x")[0]
        height = size.replace(" ","").split("x")[1]
        if width == "0" or height == "0":
            return "🔴"
        elif width != height:
            return "🟡"
        else:
            return "🟢"
    except:
        return "🔴"

def load_audio_file(filepath):
    # Load file
    try:
        audioFile = music_tag.load_file(filepath)
    except:
        return False
    titleInfo = {
        "title": str(audioFile["title"]),
        "title_safe": make_safe(str(audioFile["title"])),
        "status": check_main_tag(str(audioFile["title"]),WARN_TITLE_STRINGS)
    }
    artistInfo = {
        "artist": str(audioFile["artist"]),
        "status": check_main_tag(str(audioFile["artist"]),WARN_ARTIST_STRINGS)
    }
    albumInfo = {
        "album": str(audioFile["album"]),
        "album_safe": make_safe(str(audioFile["album"])),
        "status": check_main_tag(str(audioFile["album"]),WARN_ALBUM_STRINGS)
    }
    albumartistInfo = {
        "albumartist": str(audioFile["albumartist"]),
        "albumartist_safe": make_safe(str(audioFile["albumartist"])),
        "status": check_main_tag(str(audioFile["albumartist"]),WARN_ALBUMARTIST_STRINGS)
    }
    genreInfo = {
        "genre": str(audioFile["genre"]),
        "status": check_genre(str(audioFile["genre"]))
    }
    tracknumberInfo = {
        "tracknumber": str(audioFile["tracknumber"]),
        "totaltracks": str(audioFile["totaltracks"]),
        "status": check_number_tag(str(audioFile["tracknumber"]),0,str(audioFile["totaltracks"]))
    }
    yearInfo = {
        "year": str(audioFile["year"]),
        "status": check_number_tag(str(audioFile["year"]),1000,datetime.date.today().strftime("%Y"))
    }
    artworkInfo = {
        "status": check_artwork(audioFile),
        "size": get_artwork_size(audioFile)
    }
    audioFile["title"] = titleInfo["title"]
    audioFile.remove_tag('composer')
    audioFile.remove_tag('discnumber')
    audioFile.remove_tag('lyrics')
    audioFile.remove_tag('totaldiscs')
    #audioFile.remove_tag('tracktitle')
    audioFile.remove_tag('isrc')
    audioFile.remove_tag('compilation')

    if artworkInfo["status"] == "🟡":
        if fix_artwork(audioFile):
            artworkInfo["size"] = artworkInfo["size"]+" (Cropped)"
        else:
            artworkInfo["status"] = "🔴"
    
    if genreInfo["status"] == "🟡":
        if fix_genres(audioFile):
            genreInfo["genre"] = str(audioFile["genre"])
        else:
            genreInfo["genre"] = ""
            genreInfo["status"] = "🔴"

    with open(FILESYSTEM_PATH+"/Rejected/logfile.txt", "a") as logfile:
        logfile.write("=========="+filepath+"==========\n")
        logfile.write("Title          | "+titleInfo["status"]+" | "+titleInfo["title"]+"\nArtist         | "+artistInfo["status"]+" | "+artistInfo["artist"]+"\nAlbum          | "+albumInfo["status"]+" | "+albumInfo["album"]+"\nAlbum Artist   | "+albumartistInfo["status"]+" | "+albumartistInfo["albumartist"]+"\nGenre          | "+genreInfo["status"]+" | "+genreInfo["genre"]+"\nTrack Number   | "+tracknumberInfo["status"]+" | "+tracknumberInfo["tracknumber"]+"/"+tracknumberInfo["totaltracks"]+"\nYear           | "+yearInfo["status"]+" | "+yearInfo["year"]+"\nArtwork        | "+artworkInfo["status"]+" | "+artworkInfo["size"]+"\n")

    def get_approval_status():
        approval_status = True
        for status in [titleInfo["status"], artistInfo["status"], albumInfo["status"], albumartistInfo["status"], genreInfo["status"], tracknumberInfo["status"], yearInfo["status"], artworkInfo["status"]]:
            if status == "🔴":
                approval_status = False
        return approval_status

    if get_approval_status():
        if not os.path.isdir(FILESYSTEM_PATH+"/The Actual Playlist/"+albumartistInfo["albumartist_safe"]):
            os.mkdir(FILESYSTEM_PATH+"/The Actual Playlist/"+albumartistInfo["albumartist_safe"])
        if not os.path.isdir(FILESYSTEM_PATH+"/The Actual Playlist/"+albumartistInfo["albumartist_safe"]+"/"+albumInfo["album_safe"]):
            os.mkdir(FILESYSTEM_PATH+"/The Actual Playlist/"+albumartistInfo["albumartist_safe"]+"/"+albumInfo["album_safe"])
        
        if int(tracknumberInfo["tracknumber"]) < 10:
            fileTrackNum = "0"+tracknumberInfo["tracknumber"]
        else:
            fileTrackNum = tracknumberInfo["tracknumber"]
        audioFile.save(FILESYSTEM_PATH+"/The Actual Playlist/"+albumartistInfo["albumartist_safe"]+"/"+albumInfo["album_safe"]+"/"+fileTrackNum+". "+titleInfo["title_safe"]+"."+filepath.split(".")[-1])
        for status in [titleInfo["status"], artistInfo["status"], albumInfo["status"], albumartistInfo["status"], genreInfo["status"], tracknumberInfo["status"], yearInfo["status"], artworkInfo["status"]]:
            if status == "🟡":
                embedColor = "FFFF00"
            else:
                embedColor = "00FF00"
    else:
        embedColor = "FF0000"
        audioFile.save(FILESYSTEM_PATH+"/Rejected/"+filepath.split("/")[-1])

    webhook = DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True)
    
    with open("artwork.png", "rb") as artworkImg:
        webhook.add_file(file=artworkImg.read(), filename='artwork.png')
    os.remove('artwork.png')
    os.remove(filepath)
    embed = DiscordEmbed(title=titleInfo["title"], color=embedColor)
    embed.set_thumbnail(url="attachment://artwork.png")
    embed.add_embed_field(name="Artist(s)", value=artistInfo["artist"].replace(";",","), inline=False)
    embed.add_embed_field(name="Album", value=albumInfo["album"])
    embed.add_embed_field(name="Album Artist", value=albumartistInfo["albumartist"])
    embed.add_embed_field(name="Genre(s)", value=genreInfo["genre"].replace(";",","), inline=False)
    embed.set_footer(text=yearInfo["year"]+" • "+tracknumberInfo["tracknumber"]+"/"+tracknumberInfo["totaltracks"])
    embed.set_timestamp()
    webhook.add_embed(embed)
    response = webhook.execute()
    
while True:
    if os.path.isfile(FILESYSTEM_PATH+"/ToBeApproved/done"):
        os.remove(FILESYSTEM_PATH+"/ToBeApproved/done")
        for file in os.listdir(FILESYSTEM_PATH+"/ToBeApproved/"):
            if file.endswith(".flac") or file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".wav"):
                filepath = FILESYSTEM_PATH+"/ToBeApproved/"+str(file)
                load_audio_file(filepath)
    time.sleep(5)

