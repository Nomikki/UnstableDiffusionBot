# UnstableDiffusionBot
A simple little frontend bot

1. First, install StableDiffusion according to its instructions. You can find it here: https://github.com/AUTOMATIC1111/stable-diffusion-webui
2. Configure it to use the API.
3. Test if SD is working by generating images with it. Note: Remember to download models for it!
4. Create a Discord bot by going to https://discord.com/developers and selecting 'New Application.'
5. Give the bot permissions to read and write messages, and copy its TOKEN. Invite it to your server.
6. Clone this repository and create an `.env` file in the project's root directory. The file's content should be:
   `DISCORD_TOKEN={your bot's token}`
7. Open `bot.py` and modify the URL variable to fit your needs.
8. Run the script `python bot.py`. If you don't see any error messages in the terminal, everything should be working.
9. Test the bot's functionality in Discord by typing `/dream`.
