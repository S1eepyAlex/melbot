# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 23:39:05 2023

@author: Aleja
"""
from mailbox import Message
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import asyncio
import warnings
warnings.filterwarnings("ignore")
import re
import discord
import json
from discord.ext import commands as cds
from os.path import exists
from bs4 import BeautifulSoup
import logging
import aiohttp
import base64
from urllib.request import urlopen, Request
import emoji
from pytubefix import YouTube
import string
import random
from owoify.owoify import owoify
from owoify.owoify import Owoness

logging.basicConfig(level=logging.ERROR)


global host 
with open('host', 'r') as file:
    host = file.read().strip()

with open('token', 'r') as file:
    BOT_TOKEN = file.read().strip()

URI = f"http://{host}/v1/chat/completions"
global history 
global rules

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


if exists("history.json"):
    with open('history.json', 'r') as openfile:
        history = json.load(openfile)
else:
    history = {'history': []}
    f = open("history.json", "w")
    json_object = json.dumps(history, indent=4)
    f.write(json_object)

if exists("rules.json"):
    with open('rules.json', 'r') as openfile:
        rules = json.load(openfile)
else:
    rules = {}
    rules["change_twitter"] = True
    rules["meow"] = True
    rules["ghost_meow"] = True
    f = open("rules.json", "w")
    json_object = json.dumps(rules, indent=4)
    f.write(json_object)




bot = cds.Bot(command_prefix="!", intents=discord.Intents.all())

game = discord.Game("with statistics.")

twitter_lock = asyncio.Lock()

# def meowify(text: str) -> str:
#     words = text.split()
#     meow_sounds = ["meow", "meow!", "meow~", "purr", "mew", "MEOW"]
#     meowified_words = []
    
#     for word in words:
#         # Keep punctuation but clear it for matching case logic if needed
#         clean_word = "".join(c for c in word if c.isalnum())
        
#         # 25% chance to replace the word entirely with a meow
#         if random.random() < 0.15:
#             sound = random.choice(meow_sounds)
#             # Match capitalization style
#             if clean_word.isupper():
#                 sound = sound.upper()
#             elif clean_word.istitle():
#                 sound = sound.capitalize()
#             meowified_words.append(sound)
#         else:
#             meowified_words.append(word)
            
#             # 15% chance to inject an extra cat sound right after the word
#             if random.random() < 0.05:
#                 meowified_words.append(random.choice(meow_sounds))
                
#     return " ".join(meowified_words)

def remove_emoji(text):
    return emoji.replace_emoji(text, replace='')

def get_history_index(text: str):
    index = -1
    for i, history_obj in enumerate(history['history']):
        if text  == history_obj['content']:
            index = i
    return index

def handle_link(message_link, embedder, embeds):
    message_send = ''
    clean_link = message_link.split('?')[0]
    if not (message_link[0] == '<' and message_link[-1] == '>'):
        if '||' in clean_link:
            message_send +='||' + ('<' + clean_link +'>[.]('+ clean_link.replace(embedder, embeds[embedder]) + ")").replace('||', '') + '||\n'
        else:
            message_send += '<' + clean_link +'>[.]('+ clean_link.replace(embedder, embeds[embedder]) + ")\n"
    return message_send
    
def remove_links(text):
    url_pattern = r'https?://\S+'
    clean_text = re.sub(url_pattern, '', text).strip()
    return clean_text

def spoiler(text: str):
    return '||' + text + '||'

def sanitize_str(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.upper().replace(' ', '').replace('\n', '')
    text = "".join(dict.fromkeys(text))
    return text


async def run_chat_async(user_input, username, history_int = -1):
    headers = {
        "Content-Type": "application/json"
    }
    
    
    history["history"].append({"role": "user", "content": user_input})
    
    
    if history_int != -1:
        history_send = history["history"][:history_int]
        history_send.append({"role": "user", "content": user_input})
    else:
        history_send = history["history"]
    
    
    request = {
        "mode": "chat",
        "character": "Mel",
        "messages": history_send
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(URI, json = request, headers = headers) as response:
            if response.status == 200:
                result_json = await response.json()
                result = result_json['choices'][0]['message']
                result['content'] = result['content'].split('\n')[0]
                history["history"].append(result)
                f = open("response.json", "w")
                json_object = json.dumps(result_json, indent=4)
                f.write(json_object)
                return result
    

@bot.listen() 
async def on_message(message):
    
    if message.author.id == 318104201513140224:
        if remove_links(message.content) == '':
            await message.reply(owoify(remove_links(message.content), Owoness.Uvu) + '\n\n\\- Ghostfaggle')

    meow_str = sanitize_str(message.content)
    if meow_str[:4] in ('MEOW', 'MEWO', 'MROW', 'MIAU', 'MIAO') or meow_str[:3] in ('NYA', 'MAO'):
        await message.reply('Good kitty!')

    if message.reference:
        channel = bot.get_channel(message.reference.channel_id)
        replied_msg = await channel.fetch_message(message.reference.message_id)
        history_index = get_history_index(replied_msg.content)
        user = str(message.author.global_name)
        user_input = message.content
        if history_index != -1:
                try:
                    async with  channel.typing():
                        try:
                            result = await run_chat_async(user_input, user, history_index)
                        except:    
                            await message.reply('Text generation is unavailable.')
                        response = result['content']
                        print(history['history'][:history_index])
                        f = open("history.json", "w")
                        json_object = json.dumps(history, indent=4)
                        f.write(json_object)
                        
                        response = BeautifulSoup(response, "html.parser").prettify()
                        print("Mel: " + response)
                        
                        await message.reply(response)
                except:
                    print('Error during text gen. Please fix.')
    
    
    message_ = message.content.split()
    
    message_send = ""
    
    embeds = {
        'https://pixiv.net/': 'https://phixiv.net/',
        'https://www.pixiv.net/': 'https://phixiv.net/',
        'https://www.reddit.com/': 'https://www.vxreddit.com/',
        'https://www.tiktok.com/': 'https://www.tnktok.com/',
        'https://www.instagram.com/': 'https://www.oginstagram.com/',
        'https://bsky.app': 'https://fxbsky.app',
    }
    
    for message_link in message_:
        for embedder in embeds:
            if embedder in message_link:
                    message_send += handle_link(message_link, embedder, embeds)
    
    
    tw_links = {
        'https://twitter.com/': 'https://api.vxtwitter.com/',
        'https://x.com/': 'https://api.vxtwitter.com/'
    }
    #Twitter using vxtwt api
    
    spoiler_flag = False
    
    
    for message_link in message_:
        if message.author == bot.user or (not rules["change_twitter"]):
            return 
        for link in tw_links:
            if link in message_link:
                    # twitter_lock.acquire()
                    
                    spoiler_flag = False
                    if '||' in message_link:
                        spoiler_flag = True
                        message_link = message_link.replace('||', '')
                    
                    clean_link = message_link.split('?')[0]
                    async with aiohttp.ClientSession() as session:
                            async with session.get(clean_link.replace(link, tw_links[link])) as response:
                                r = await response.json()
                                tweet_media = r['mediaURLs']
                            
                                if not r['hasMedia']:
                                    vx_link = handle_link(message_link, link, tw_links).replace('api.', '')
                                    if spoiler_flag:
                                        vx_link = spoiler(vx_link)
                                    message_send += vx_link
                                
                                else: 
                                    author = remove_emoji(r['user_screen_name'])
                                    author = re.sub('_+', '_', author)
                                    tweet_text = f'[{author}](<{clean_link}>):'
                                    raw_tweet_text = r['text']
                                    tweet_text_array = raw_tweet_text.split(' ')
                                    if not (raw_tweet_text is None or (len(tweet_text_array) == 1 and 'https://t.co/' in tweet_text_array[0])):
                                        tweet_text += '\n'
                                    for word in tweet_text_array:
                                        if not 'https://t.co/' in word:
                                            tweet_text += word + ' '
                                    if len(raw_tweet_text) >= 280:
                                        tweet_text = tweet_text[:-1] + '...'
                                    
                                    if not (tweet_text == '' or tweet_text is None):
                                        if not r['qrt'] == None:
                                            quote_author = remove_emoji(r['qrt']['user_screen_name'])
                                            qrt_link = r['qrt']['tweetURL']
                                            quote_text = f'> [{quote_author}](<{qrt_link}>):'
                                            raw_quote_text = r['qrt']['text']
                                            quote_text_array = raw_quote_text.split(' ')
                                            
                                            filtered_text = ''
                                            for word in quote_text_array:
                                                if not 'https://t.co/' in word:
                                                    filtered_text += word + ' '
                                            paragraphs = filtered_text.split('\n')
                                            for paragraph in paragraphs:
                                                if not  paragraph == '': quote_text += '\n> ' + paragraph
                                            
                                            if len(raw_quote_text) >= 280:
                                                quote_text = quote_text[:-1] + '...'
                                            
                                            tweet_text += f'\n{quote_text}'
                                        
                                        message_send_twitter = f'{tweet_text}\n'
                                    
                                    
                                        # try: 
                                        files = []
                                        for i, media_link in enumerate(tweet_media):
                                            name_dc = media_link.split('/')[-1]
                                            if 'https://pbs.twimg.com' in media_link:
                                                print(media_link)
                                                filename = f'attachments/Attachment {i}.jpg'        
                                            else:
                                                print(media_link)
                                                filename = f'attachments/Attachment {i}.mp4'
                                            with urlopen(Request(media_link, headers=hdr)) as f:
                                                with open(filename, 'wb') as f2:
                                                    f2.write(f.read())
                                                dc_file = discord.File(filename)
                                                dc_file.filename = name_dc
                                                files.append(dc_file)
                                        # except Exception as e:
                                        #     print(e)
                                        #     message_send_twitter += 'Media links:\n'
                                        #     for i, media_link in enumerate(tweet_media):
                                        #         message_send_twitter += f'[{i+1}]({media_link})\n'
                                    
                                    
                                    if spoiler_flag:
                                        message_send_twitter = '||' + message_send_twitter + '||'
                                        for i in range(len(files)):
                                            files[i].filename = f"SPOILER_{files[i].filename}"         
									
                                    await message.channel.send(content = message_send_twitter, files = files)
                                    await message.edit(suppress=True)
                    # twitter_lock.release()
                                        
    
    if message_send == '':
        return
    
    print(message_send)
    await message.channel.send(content = message_send)
    await message.edit(suppress=True)
    
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=game)

@bot.command()
async def check(ctx):
    print(ctx.author.global_name)

@bot.command()
async def musk(ctx):
    dc_file = discord.File('musk.mp4')
    await ctx.channel.send(files = [dc_file])


@bot.slash_command(
    name="image",
    guild_ids=[900229825137086474, 546515996618391562]
)
async def image(ctx, prompt, steps = 20, width = 1024, height = 1024):  
    await ctx.response.defer()
    url = "http://127.0.0.1:7860"
    
    prompt_enhanced = 'score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, rating_safe, ' + prompt
    neg_prompt = 'FastNegativeV2, (low quality:1.3), (worst quality:1.3),(monochrome:0.8),(deformed:1.3),(malformed hands:1.4),(poorly drawn hands:1.4),(mutated fingers:1.4),(bad anatomy:1.3),(extra limbs:1.35),(poorly drawn face:1.4),(watermark:1.3)'
    
    request = {
        'prompt': prompt_enhanced,
        'negative_prompt': neg_prompt,
        'steps': steps,
        'width': width,
        'height': height,
        'sampler_name': 'DPM++ 2M SDE',
        'sd_model_checkpoint': 'ponyDiffusionV6XL',
        "enable_hr": False,
        "hr_second_pass_steps": 20,
        "denoising_strength": 0.6
    }
    try: 
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f'{url}/sdapi/v1/txt2img', json = request) as response:
                    if response.status == 200:
                        r = await response.json()
            except:
                await ctx.followup.send('Image generation is not availale.')
        print(f'{ctx.author.display_name}: {prompt}')
        
        with open("output_landscape.png", 'wb') as f:
            f.write(base64.b64decode(r['images'][0]))
        
        await ctx.followup.send(f'Prompt: {prompt}', file = discord.File('output_landscape.png'))    
    except:
        await ctx.followup.send('An unexpected error ocurred.')
    
@bot.slash_command(
    name="yt_download",
    guild_ids=[900229825137086474, 546515996618391562]
)
async def yt_download(ctx, link):
    await ctx.response.defer()
    
    myVideo = YouTube(link)
    myVideo.streams.get_highest_resolution().download(filename='yt_download.mp4')
    
    await ctx.followup.send(file = discord.File('yt_download.mp4'))    


embeds = discord.SlashCommandGroup("embeds", "Enable or disable embedding")

@embeds.command()
async def enable(ctx):
    rules["change_twitter"] = True
    await ctx.respond("Site embedding enabled.")
    
    f = open("rules.json", "w")
    json_object = json.dumps(rules, indent=4)
    f.write(json_object)

@embeds.command()
async def disable(ctx):
    rules["change_twitter"] = False
    await ctx.respond("Site embedding disabled.")
    
    f = open("rules.json", "w")
    json_object = json.dumps(rules, indent=4)
    f.write(json_object)

bot.add_application_command(embeds)

@bot.slash_command(
    name="erase_history",
    guild_ids=[900229825137086474, 546515996618391562]
)
async def erase_history(ctx):
    history["history"] = []
    await ctx.respond("History erased!")

@bot.slash_command(
    name="talk",
    guild_ids=[900229825137086474, 546515996618391562]
)
async def talk(ctx):
    await ctx.response.defer()
    
    user = str(ctx.author.global_name)
    
    user_input = 'Hi!'
    try:
        async with ctx.typing():
            try:
                result = await run_chat_async(user_input, user)
            except:    
                await ctx.followup.send('Text generation is unavailable.')
        response = result['content']
        
        f = open("history.json", "w")
        json_object = json.dumps(history, indent=4)
        f.write(json_object)
        
        response = BeautifulSoup(response, "html.parser").prettify()
        print("Mel: " + response)
        
        await ctx.followup.send(response)
    except:
        await ctx.followup.send('An unexpected error ocurred.')
    
    

bot.run(BOT_TOKEN)
logging.basicConfig(level=logging.ERROR)
