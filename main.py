from discord.ext import commands
import discord
from zen_quote import *
from quozio_quote import QuozioImageCollector
from exceptions import AuthorError, QuoteError, TemplateError
import personal_vars # Holds only bot token. You will need your own bot token for this to work

client = commands.Bot(command_prefix='!', help_command=None)

NAMES_FILE = "famous_names.txt"
TEMPLATE_FILE = "valid_template_ids.txt"
IMG_FILE_NAME = "quote_image.jpeg"


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('!Help'))
    print(f'Logged in as {client.user}\n')


# Sends an embed to the channel about how to use the bot
@client.command(aliases=['Help'])
async def help(context):
    embed = discord.Embed(title="!Help")
    embed.add_field(name="!Add_Name", 
                    value='Follow the command with a name of your choice. Adds the name to the list of authors !Insight can pick from.', 
                    inline=False)
    embed.add_field(name="!Remove_Name", 
                    value='Follow the command with a name of your choice. Removes the name to the list of authors !Insight can pick from.', 
                    inline=False)
    embed.add_field(name="!Clear_Names", 
                    value='Removes all names from the names file.', 
                    inline=False)
    embed.add_field(name="!Fetch_Templates", 
                    value='Collects the image templates from Quozio.com to use with the quotes.', 
                    inline=False)
    embed.add_field(name="!Insight", 
                    value='Returns an inspiring quote image, with a random author picked from names you\'ve added.', 
                    inline=False)
                    
    await context.send(embed=embed)


# Command to add names to the names file
@client.command(aliases=['Add_Name', 'Add_name'])
async def add_name(context, *, name_to_add):
    name_to_add = name_to_add.title()

    with open(NAMES_FILE, 'r') as file:
        famous_names = file.readlines()

    if name_to_add not in famous_names:
        with open(NAMES_FILE, 'a') as file:
            file.write(f"{name_to_add}\n")
        await context.send("Name added.")

    else:
        await context.send("Name already added.")


# Command to remove names from the names file
@client.command(aliases=['Remove_Name', 'Remove_name'])
async def remove_name(context, *, name_to_remove):
    name_to_remove = name_to_remove.title()

    try:
        with open(NAMES_FILE, 'r') as file:
            famous_names = file.readlines()

        if f"{name_to_remove}\n" in famous_names:
            with open(NAMES_FILE, 'w') as file:
                for name in famous_names:
                    if name.strip("\n") != name_to_remove:
                        file.write(name)
            await context.send("Name removed.")

        else:
            await context.send("Name not found.")

    except FileNotFoundError:
        await context.send("No current author file. Use !add_name followed by a name of your choice first.")


# command to remove all names from the names file
@client.command(aliases=['Clear_Names', 'Clear_names'])
async def clear_names(context):
    try:
        file = open(NAMES_FILE, 'w')
        file.close()
        await context.send("All names cleared.")

    except FileNotFoundError:
        await context.send("No current author file. Use !add_name followed by a name of your choice first.")


# Command to retreive template IDs from Quozio.com
@client.command(alises=['Fetch_Templates', 'Fetch_templates'])
async def fetch_templates(context):
    await context.send("Retrieving quote templates from quozio.com, please wait...")
    try:
        base_collector = QuozioImageCollector(TEMPLATE_FILE, "quote", "author")
        base_collector.list_tmpl_ids()
        await context.send("Templates retrieved! Use \"!insight\" to get a quote.")
    except QuoteError:
        await context.send("Could not reteive all quote templates. Try again later.")


# Command to post an inspiring quote image in the text channel
@client.command(aliases=['Insight'])
async def insight(context):
    try:
        quote = get_quote()
        author = get_author(NAMES_FILE)

        q = QuozioImageCollector(TEMPLATE_FILE, quote, author)
        q.collect(IMG_FILE_NAME)

        with open(IMG_FILE_NAME, 'rb') as file:
            quote_image = discord.File(file)
            await context.send(file=quote_image)

    except QuoteError:
        await context.send('Could not retreive quote.')

    except AuthorError:
        await context.send('No logged authors. Must use !add_name followed by a name of your choice first.')

    except TemplateError:
        await context.send('No templates found. Must use !fetch_templates first.')


if __name__ == '__main__':
    client.run(personal_vars.TOKEN)