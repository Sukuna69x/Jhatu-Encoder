#ffmpeg.py
import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

import asyncio
import os
import time
import re
import json
import subprocess
import math
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.helper_funcs.display_progress import (
  TimeFormatter
)
from bot.localisation import Localisation
from bot import (
    FINISHED_PROGRESS_STR,
    UN_FINISHED_PROGRESS_STR,
    DOWNLOAD_LOCATION,
    crf,
    resolution,
    audio_b,
    preset,
    codec,
    watermark,
    pid_list
)

def get_full_filename(filepath):
    # Get full filename without first-word limitation
    return os.path.splitext(os.path.basename(filepath))[0]

async def convert_video(video_file, output_directory, total_time, bot, message, chan_msg, custom_filename=None):
    file_name = get_full_filename(video_file)  # Use the new method
    file_ext = os.path.splitext(os.path.basename(video_file))[1]  # Split extension

    # Handle custom filename
    if custom_filename:
        out_put_file_name = os.path.join(output_directory, f"{custom_filename}{file_ext}")
    else:
        out_put_file_name = os.path.join(output_directory, f"{file_name}{file_ext}")

    progress = os.path.join(output_directory, "progress.txt")
    with open(progress, 'w') as f:
        pass

    # Rest of the existing code remains the same
    crf.append("28")
    codec.append("libx264")
    resolution.append("854x480")
    preset.append("veryfast")
    audio_b.append("40k")
    file_genertor_command = f"ffmpeg -hide_banner -loglevel quiet -progress '{progress}' -i '{video_file}' -metadata 'title=Encoded by Anime Empire' -c:v {codec[0]} -map 0 -crf {crf[0]} -c:s copy -pix_fmt yuv420p -s {resolution[0]} -b:v 500k -c:a libopus -b:a {audio_b[0]} -preset {preset[0]} -metadata:s:v 'title=Anime Empire' -metadata:s:a 'title=Anime Empire' -metadata:s:s 'title=Anime Empire' -vf 'drawtext=fontfile=font.ttf:fontsize=32:fontcolor=white@0.4:x=10:y=10:text=Anime Empire' '{out_put_file_name}' -y"
    
    # Execute the compression process
    COMPRESSION_START_TIME = time.time()
    process = await asyncio.create_subprocess_shell(
        file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    LOGGER.info(f"ffmpeg_process: {process.pid}")
    pid_list.insert(0, process.pid)
    status = os.path.join(output_directory, "status.json")
    with open(status, 'r+') as f:
        status_msg = json.load(f)
        status_msg['pid'] = process.pid
        status_msg['message'] = message.id
        f.seek(0)
        json.dump(status_msg, f, indent=2)
    # os.kill(process.pid, 9)
    isDone = False
    while process.returncode != 0:
      await asyncio.sleep(3)
      with open(DOWNLOAD_LOCATION + "/progress.txt", 'r+') as file:
        text = file.read()
        frame = re.findall("frame=(\d+)", text)
        time_in_us=re.findall("out_time_ms=(\d+)", text)
        progress=re.findall("progress=(\w+)", text)
        speed=re.findall("speed=(\d+\.?\d*)", text)
        if len(frame):
          frame = int(frame[-1])
        else:
          frame = 1;
        if len(speed):
          speed = speed[-1]
        else:
          speed = 1;
        if len(time_in_us):
          time_in_us = time_in_us[-1]
        else:
          time_in_us = 1;
        if len(progress):
          if progress[-1] == "end":
            LOGGER.info(progress[-1])
            isDone = True
            break
        execution_time = TimeFormatter((time.time() - COMPRESSION_START_TIME)*1000)
        elapsed_time = int(time_in_us)/1000000
        difference = math.floor( (total_time - elapsed_time) / float(speed) )
        ETA = "-"
        if difference > 0:
          ETA = TimeFormatter(difference*1000)
        percentage = math.floor(elapsed_time * 100 / total_time)
        progress_str = "♻️ **ᴘʀᴏɢʀᴇss**: {0}%\n[{1}{2}]".format(
            round(percentage, 2),
            ''.join([FINISHED_PROGRESS_STR for i in range(math.floor(percentage / 10))]),
            ''.join([UN_FINISHED_PROGRESS_STR for i in range(10 - math.floor(percentage / 10))])
            )
        stats = f'⚡ **ᴇɴᴄᴏᴅɪɴɢ ɪɴ ᴘʀᴏɢʀᴇss**\n\n' \
                f'🕛 **ᴛɪᴍᴇ ʟᴇғᴛ**: {ETA}\n\n' \
                f'{progress_str}\n'
        try:
          await message.edit_text(
            text=stats,
            reply_markup=InlineKeyboardMarkup(
                [
                    [ 
                        InlineKeyboardButton('❌ Cancel ❌', callback_data='fuckingdo') # Nice Call 🤭
                    ]
                ]
            )
          )
        except:
            pass
        try:
          await bug.edit_text(text=stats)
        except:
          pass
        
    stdout, stderr = await process.communicate()
    r = stderr.decode()
    try:
        if er:
           await message.edit_text(str(er) + "\n\n**ERROR** Contact @Sensei_Rimuru")
           os.remove(videofile)
           os.remove(out_put_file_name)
           return None
    except BaseException:
            pass
    #if( not isDone):
      #return None
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(e_response)
    LOGGER.info(t_response)
    del pid_list[0]
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None

async def media_info(saved_file_path):
  process = subprocess.Popen(
    [
      'ffmpeg', 
      "-hide_banner", 
      '-i', 
      saved_file_path
    ], 
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT
  )
  stdout, stderr = process.communicate()
  output = stdout.decode().strip()
  duration = re.search("Duration:\s*(\d*):(\d*):(\d+\.?\d*)[\s\w*$]",output)
  bitrates = re.search("bitrate:\s*(\d+)[\s\w*$]",output)
  
  if duration is not None:
    hours = int(duration.group(1))
    minutes = int(duration.group(2))
    seconds = math.floor(float(duration.group(3)))
    total_seconds = ( hours * 60 * 60 ) + ( minutes * 60 ) + seconds
  else:
    total_seconds = None
  if bitrates is not None:
    bitrate = bitrates.group(1)
  else:
    bitrate = None
  return total_seconds, bitrate
  
async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = os.path.join(
        output_directory,
        str(time.time()) + ".jpg"
    )
    if video_file.upper().endswith(("MKV", "MP4", "WEBM")):
        file_genertor_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            video_file,
            "-vframes",
            "1",
            out_put_file_name
        ]
        
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
    #
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
# senpai I edited this,  maybe if it is wrong correct it 
def get_width_height(video_file):
    metadata = extractMetadata(createParser(video_file))
    if metadata.has("width") and metadata.has("height"):
        return metadata.get("width"), metadata.get("height")
    else:
        return 1280, 720
