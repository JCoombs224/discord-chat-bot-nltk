import asyncio
import discord
import os
import random
import requests
from prompts import compliments
from prompts import insults
from discord import FFmpegPCMAudio
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

RNG_THRESHOLD = 5

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Well here I am!')
        break
    
# Function to play a sound
async def join_and_play(voice_channel, sound_file):
  try:
    if os.path.exists(sound_file):
      print("Sound file found!")
      voice_client = await voice_channel.connect()
      print("Bot has joined the voice channel.")
      # source = FFmpegPCMAudio(sound_file, options="-filter:a 'volume=2.0'")
      source = FFmpegPCMAudio(sound_file)
      voice_client.play(source)

      while voice_client.is_playing():
        await asyncio.sleep(1)

      await voice_client.disconnect()
      print("Bot has left the voice channel.")
    else:
      print("Sound file not found!")
  except Exception as e:
      print(f"Error joining or playing sound: {e}")

async def send_insult(message, use_api=True):
  print('insulting ' + message.author.name)
  # set bot to typing
  await message.channel.typing()

  # wait for bot to finish typing
  await asyncio.sleep(5)

  if use_api:
    insult = "{} " + requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=plaintext').text
  else:
    insult = "{} " + random.choice(insults)
  await message.reply(insult.format(message.author.mention))

async def send_compliment(message):
  print('complimenting ' + message.author.name)
  # set bot to typing
  await message.channel.typing()

  # wait for bot to finish typing
  await asyncio.sleep(5)

  compliment = "{} " + random.choice(compliments)
  await message.reply(compliment.format(message.author.mention))

async def analyze(user_input):
  sia = SentimentIntensityAnalyzer()
  return sia.polarity_scores(user_input)

@client.event
async def on_message(message):
  if message.author == client.user or message.author == 415380635343912972:
    return

  rng = random.randrange(0, 100, 1)
  print(rng)
  await asyncio.sleep(1)

  rng_threshold = RNG_THRESHOLD

  # Check if bot is mentioned in message
  if client.user.mentioned_in(message) or 'david' in message.content.lower() or 'dave' in message.content.lower():
    if 'join' in message.content.lower() and message.author.voice:
      voice_channel = message.author.voice.channel
      sound_file = '/home/jcoombs/scripts/breath' + str(random.randrange(1, 3, 1)) + '.mp3' 
      await join_and_play(voice_channel, sound_file)
      return
    sentiment = await analyze(message.content)
    print(sentiment)
    if sentiment['compound'] >= 0.25:
      await send_compliment(message)
    elif sentiment['compound'] < 0.25:
      use_insult_api = rng >= rng_threshold/2
      await send_insult(message, use_insult_api)
    return
  
  # bot was not mentioned, so we just use rng now
  if message.author.name == 'friedeggs0106' or message.author.name == 'zenitsu2342':
    rng_threshold = 38

  if rng <= 1 or (message.author.name == 'yungmokee' and rng < 38):
    await send_compliment(message)
    return
  
  if rng < rng_threshold:
    use_insult_api = rng >= rng_threshold/2
    await send_insult(message, use_insult_api)

client.run(os.getenv("DISCORD_API_KEY"))
