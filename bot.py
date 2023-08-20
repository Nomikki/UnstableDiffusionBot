# bot.py
import os
import random
from typing import Optional

from discord.ext import commands
from dotenv import load_dotenv

import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import discord
from discord import option


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
URL = "http://127.0.0.1:9000"


bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

currentPrompt = ""
currentNegativePrompt = ""
currentSteps = 32
currentSeed = -1
currentSampler = "Euler a"
currentScale = 7
currentBatchSize = 1
currentFaceFix = ""
currentDataModel: str = ""

samplerNames = []
faceFixes = []
sdModels = []


@bot.slash_command(name='dream')
@option(
    'prompt',
        str,
        description='A prompt to condition the model with.',
        required=True,
    )
@option(
        'negative_prompt',
        str,
        description='Negative prompts to exclude from output.',
        required=False,
    )
@option(
        'data_model',
        str,
        description='Select the data model for image generation.',
        required=False,
        autocomplete=discord.utils.basic_autocomplete(sdModels),
    )
@option(
        'steps',
        int,
        description='The amount of steps to sample the model.',
        min_value=1,
        required=False,
    )
@option(
        'guidance_scale',
        str,
        description='Classifier-Free Guidance scale.',
        required=False,
    )
@option(
        'sampler',
        str,
        description='The sampler to use for generation.',
        required=False,
        autocomplete=discord.utils.basic_autocomplete(samplerNames),
    )
@option(
        'seed',
        int,
        description='The seed to use for reproducibility.',
        required=False,
    )
@option(
        'facefix',
        str,
        description='Tries to improve faces in images.',
        required=False,
        autocomplete=discord.utils.basic_autocomplete(faceFixes),
    )
@option(
        'batch',
        str,
        description='The number of images to generate. Batch format: count,size',
        required=False,
    )
async def gene(ctx, prompt: str,
                    negative_prompt: str = None, 
                    data_model: str = None,
                    steps: int = None,
                    guidance_scale: str = None,
                    sampler: str = None,
                    seed: int = -1,
                    facefix: str = None,
                    batch: str = None
                    ):
    
    global currentDataModel

    if negative_prompt is None:
        negative_prompt = currentNegativePrompt
        
    if steps is None:
        steps = currentSteps
    
    if guidance_scale is None:
        guidance_scale = currentScale
    
    if sampler is None:
        sampler = currentSampler
    
    if facefix is None:
        facefix = currentFaceFix

    if batch is None:
        batch = currentBatchSize
        
    if seed is None:
        seed = currentSeed

    if seed == -1:
        seed = random.randint(0, 0xFFFFFFFF)


    reply_adds = "\n"
    reply_adds += f'prompt: {prompt}\n'
    reply_adds += f'negative prompt: {negative_prompt}\n'
    reply_adds += f'steps: {steps}\n'
    reply_adds += f'guidance: {guidance_scale}\n'
    reply_adds += f'sampler: {sampler}\n'
    reply_adds += f'face fix: {facefix}\n'
    reply_adds += f'batch: {batch}\n'

    reply_adds += f'seed: {seed}\n'


    response = f'krunts krunts... seed: {seed} - ``{reply_adds}``'
    await ctx.send_response(response);
    
    if data_model != None:
        if data_model != currentDataModel:
            model_payload = {
                "sd_model_checkpoint": data_model
            }
            response = requests.post(url=f'{URL}/sdapi/v1/options', json=model_payload)
            r = response.json()
            await ctx.respond("model changed")    
        
        currentDataModel = data_model
        
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "sampler_index": sampler,
        "cfg_scale": guidance_scale,
        "batch_size": batch,
        "seed": seed,
    }

    # add any options that would go into the override_settings
    override_settings = {"CLIP_stop_at_last_layers": 1}

    if facefix != 'None':
        override_settings["face_restoration_model"] = facefix
        # face restoration needs this extra parameter
        facefix_payload = {
            "restore_faces": True,
        }
        payload.update(facefix_payload)

    # update payload with override_settings
    override_payload = {
        "override_settings": override_settings
        }
    payload.update(override_payload)
    

    #print(payload)

    response = requests.post(url=f'{URL}/sdapi/v1/txt2img', json=payload)
    r = response.json()
        
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
    
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{URL}/sdapi/v1/png-info', json=png_payload)
    
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save('output.png', pnginfo=pnginfo)
        await ctx.send(file=discord.File('output.png'))
    
    



    await ctx.respond('done! ^_^')


@bot.event
async def on_ready():

    r1 = requests.get(url=f'{URL}/sdapi/v1/samplers')
    r3 = requests.get(url=f'{URL}/sdapi/v1/face-restorers')
    r5 = requests.get(url=f'{URL}/sdapi/v1/sd-models')

    for s1 in r1.json():
        samplerNames.append(s1['name'])

    for s3 in r3.json():
        faceFixes.append(s3['name'])

    for s5 in r5.json():
        sdModels.append(s5["model_name"])

    print(samplerNames)
    print(faceFixes)
    print(sdModels)
    print("I'm ready! \o/")

bot.run(TOKEN)
