try:
    from utils.PackageHandler import auto_install_missing_packages
    from utils.Colors import Colors
    print(f'[{Colors.GREEN}{Colors.BOLD}LOGS{Colors.RESET}] Verifying packages...')
    auto_install_missing_packages()
    
    import discord
    from discord.ext import commands
    import os
    import asyncio
    from utils.config import basicconfig


    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix=basicconfig.PREFIX, intents=intents)
    bot.help_command = None

    loaded_extensions = []



    # Loading all the cogs
    async def load_all_extensions():
        """Asynchronously loads all the extensions (cogs) from the cogs folder."""
        
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                extension = f"cogs.{filename[:-3]}"
                if extension in bot.extensions:
                    continue
                await bot.load_extension(extension)
                print(f"[{Colors.GREEN}{Colors.BOLD}LOGS{Colors.RESET}] Successfully loaded {filename[:-3]}")
            else:
                pass


    @bot.event
    async def on_ready():

        await load_all_extensions()
        synced = await bot.tree.sync()
        print(f"[{Colors.GREEN}{Colors.BOLD}LOGS{Colors.RESET}] Successfully synced all slash commands")
        print(
        f'''\n
        BOT IS ONLINE! ({bot.user})
    \n''')
            

        


    @bot.command()
    @commands.has_permissions(administrator=True)
    async def sync(ctx):
        await bot.tree.sync()
        await ctx.reply('**Successfully synced all the slash commands**')

    # Load a cog
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def loadcog(ctx, cogname: str = None):
        if cogname:
            try:
                await bot.load_extension(f'cogs.{cogname}')
                await ctx.send(f'Loaded {cogname} cog successfully.')
            except Exception as e:
                await ctx.send(f'Error loading {cogname} cog: {e}')
        else:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await bot.load_extension(f'cogs.{filename[:-3]}')
            await ctx.send('Loaded all cogs successfully.')

    # Unload a cog
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def unloadcog(ctx, cogname: str = None):
        if cogname:
            try:
                await bot.unload_extension(f'cogs.{cogname}')
                await ctx.send(f'Unloaded {cogname} cog successfully.')
            except Exception as e:
                await ctx.send(f'Error unloading {cogname} cog: {e}')
        else:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await bot.unload_extension(f'cogs.{filename[:-3]}')
            await ctx.send('Unloaded all cogs successfully.')

    @bot.command()
    async def reloadcog(ctx, cogname: str):
        try:
            await bot.reload_extension(f'cogs.{cogname}')
            await ctx.reply(f'Reloaded {cogname} cog successfully.')
        except Exception as e:
            await ctx.reply(f'Error Reloading {cogname} cog: {e}')




    import logging
    from datetime import datetime

    # Ensure the Logs directory exists
    log_dir = "Logs"
    os.makedirs(log_dir, exist_ok=True)

    # Rename 'latest.log' if it exists
    latest_log_path = os.path.join(log_dir, "latest.log")
    if os.path.exists(latest_log_path):
        # Create a new name for the old log file with Date-Time format
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_log_name = f"{timestamp}.log"
        new_log_path = os.path.join(log_dir, new_log_name)
        os.rename(latest_log_path, new_log_path)

    # Set up the logging handler for 'latest.log'
    handler = logging.FileHandler(filename=latest_log_path, mode="w", encoding="utf-8")

    # Start the bot with custom log handler
    bot.run(token=basicconfig.TOKEN, log_handler=handler)

except discord.errors.LoginFailure:
    class Wrong_Config(Exception):
        pass
    raise Wrong_Config('\n\n\n------------------[ERROR]-----------------\nPlease configure your bot in the config.yml file\nPossible causes of this error:\n- Wrong TOKEN in config.yml.\n- Config.yml file was missing so the bot created a new one. (Could be this reason if you are starting the bot for the first time)\n- The format for config.yml was wrong so the bot replaced it with the default config file Please reconfigure it\n\nPossible solution: Just follow the instructions in the config.yml file correctly\n\n')
