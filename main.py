import ffmpeg
import os
import pathlib
import asyncio
import time
import random
import math
import itertools

async def play(video, section):
    global key, url
    
    x = list(pathlib.Path(f"./Files/{section}").glob("*"))
    h = [i for i in x if i.name[0] != "."]
    genre = random.choice(h)
    
    song_files = [i for i in genre.glob("*.*") if i.name[0] != "."]
    #random.shuffle(song_files)
    song = random.choice(song_files)
    
    #song_durations = [float(ffmpeg.probe(str(i))["streams"][0]["duration"]) for i in song_files]
    song_durations = [float(ffmpeg.probe(str(song))["streams"][0]["duration"])]
    
    #inputs = [ffmpeg.input(str(i), readrate=1) for i in song_files]
    #final_audio = ffmpeg.concat(*inputs, v=0, a=1)
    final_audio = ffmpeg.input(str(song), readrate=1)
    
    video = ffmpeg.input(str(video), stream_loop=-1, readrate=1)
    video = ffmpeg.concat(video, v=1, a=0)
    
    video = video.drawtext(text=f"Section: {section}\nGenre: {genre.name}\nAudio: {song.name}",
                           x=50, y=50,
                           box=1, boxcolor="black@0.45", boxborderw=15,
                           fontcolor="white", fontsize=30, fix_bounds=True
                           )

    """"
    acc_duration = 0
    for i in song_files:
        duration = float(ffmpeg.probe(str(i))["streams"][0]["duration"])
        song_name = "".join(i.name.split(".")[:-1])
        video = video.drawtext(text=f"Section: {section}\nGenre: {genre.name}\nAudio: {song_name}", 
                           x=50, y=50, 
                           box=1, boxcolor="black@0.45", boxborderw=15,
                           fontcolor="white", fontsize=60, fix_bounds=True, 
                           enable=f"between(t,{acc_duration},{acc_duration+duration})")
        acc_duration += duration
    """
    result = ffmpeg.output(final_audio, video, url+"/"+key, format="flv", t=sum(song_durations))#.global_args("-re")#.global_args("-r 25")
    return result, sum(song_durations)

sections_list = [i for i in pathlib.Path("./Files").iterdir() if i.name[0] != "." and i.is_dir()]
sections_list.sort()
videos = pathlib.Path("./Videos")

settings_text = open("settings.txt").readlines()
settings = {}
for i in settings_text:
    temp = i.strip().split("=")
    if temp[0] == "":
        continue
    settings[temp[0]] = temp[1]

url = settings["url"]
key = settings["key"]
ffmpegoutputnoise = settings["ffmpeg_quiet"] == "True"

current_section = sections_list[0]
while True:
    a, t = asyncio.run(play(random.choice([i for i in pathlib.Path("./Videos").iterdir() if i.name[0] != "." and i.is_file()]) , current_section.name))
    print(current_section.name, sections_list)
    a.run_async(quiet=ffmpegoutputnoise)
    time.sleep(t)
    sections_list = [i for i in pathlib.Path("./Files").iterdir() if i.name[0] != "." and i.is_dir()]
    sections_list.sort()
    i = sections_list.index(current_section)
    if i == len(sections_list) - 1:
        current_section = sections_list[0]
    else:
        current_section = sections_list[i+1]
exit()
