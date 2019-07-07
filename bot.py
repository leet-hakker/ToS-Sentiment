import pickle
import os
import discord
from discord.ext import commands
from discord.ext.commands import bot
from discord.utils import get
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions

command_prefix = '!'
colour = 0x41d8a7
client = commands.Bot(command_prefix)


def extract_features(word_list):
    return dict([(word, True) for word in word_list])


classifier = pickle.load(open('<YOUR_MODEL>', 'rb'))

blacklist = [
    "Nigger", "Fagot", "Faggot", "Fagit", "Faggit", "Chink", "Spick", "Nigga",
    "Fag"
]


@client.event
async def on_ready():
    print("Ready")
    await client.change_presence(
        activity=discord.Game(name="with the souls of the damned", type=1))


@client.event
async def on_message(ctx):
    content = ctx.content
    if content.startswith(command_prefix):
        client.process_commands
    author = ctx.author
    probdist = classifier.prob_classify(extract_features(content.split()))
    pred_sentiment = probdist.max()
    print(content)
    print("Predicted sentiment:", pred_sentiment)
    print("Probability:", round(probdist.prob(pred_sentiment), 2))
    if pred_sentiment == 'Negative':
        for i in blacklist:
            if i.lower() in content.lower():
                await ctx.delete(delay=None)
                await ctx.channel.send(
                    author.mention +
                    " do you kiss your mother with that mouth?")
                embed = discord.Embed(
                    title=f"Filter activated for user {author}",
                    description=content,
                    color=colour)
                embed.add_field(name="Triggered on:", value=f"{i}")
                await ctx.channel.send(embed=embed)
                break


@client.command(name='release', pass_context=True)
@has_permissions(manage_roles=True)
async def release(ctx, user: discord.Member):
    await ctx.message.delete()

    def check(reaction, author):
        return author == user and str(reaction.emoji) == '✅'

    embed = discord.Embed(
        title=f'Releasing {user.name}',
        description=
        f'{user.mention}, you are being released upon the following condition(s):',
        color=colour)
    conditions = ctx.message.content[9:].strip(f'{user.mention}').split('|')
    for i in range(len(conditions)):
        embed.add_field(name=f'{i+1}:', value=conditions[i], inline=False)

    embed.set_footer(
        text=
        'By reacting to this message with ✅, you confirm that you understand and agree to the above condition(s).'
    )
    msg = await ctx.channel.send(embed=embed)

    await msg.add_reaction('✅')
    reaction, user = await client.wait_for('reaction_add', check=check)
    await user.remove_roles(get(ctx.message.guild.roles, name='ranched'))


@release.error
async def release_error(error, ctx):
    if isinstance(error, MissingPermissions):
        await ctx.channel.send('You do not have sufficient permissions.')


client.run(os.getenv('TOKEN'))
