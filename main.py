import discord
import discord.app_commands as commands
import json

def load():
    with open(file='./config/config.json', mode='r', encoding='utf-8') as file:
        return json.loads(file.read())

def save(config):
    with open(file='./config/config.json', mode='w', encoding='utf-8') as file:
        file.write(json.dumps(config, indent=4))

config = load()
print(config)
token = config['token']

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = commands.CommandTree(bot)

# コマンド実装
@tree.command(name="edit_join_message", description="メンバーが参加したときに送信するメッセージを編集します")
@commands.describe(title="参加時に送信するembedのタイトル")
@commands.describe(text="参加時に送信するembedの本文")
async def edit_join_message(interaction: discord.Interaction, title: str, text: str):
    await interaction.response.defer()

    for role in interaction.user.roles:
        if role.permissions.administrator:
            # 処理を書く
            config['Wisdom']['message']['join_message']['title'] = title
            config['Wisdom']['message']['join_message']['description'] = text
            save(config)

            embed = discord.Embed(
                title="Done",
                description="### メッセージの編集に成功しました\n反映には時間がかかる可能性がございます\n### 内容\nTitle: {}\nText: {}".format(title, text),
                color=discord.Color.green()
            )

            await interaction.followup.send(embed=embed)
            return

    embed = discord.Embed(
        title="Error",
        description="You don't have permission to edit this message",
        color=discord.Color.red()
    )

    await interaction.followup.send(embed=embed)
    return

@tree.command(name="edit_left_message", description="メンバーが脱退したときに送信するメッセージを編集します")
@commands.describe(title="脱退時に送信するembedのタイトル")
@commands.describe(text="脱退時に送信するembedの本文")
async def edit_left_message(interaction: discord.Interaction, title: str, text: str):
    await interaction.response.defer()

    for role in interaction.user.roles:
        if role.permissions.administrator:
            # 処理を書く
            config['Wisdom']['message']['left_message']['title'] = title
            config['Wisdom']['message']['left_message']['description'] = text
            save(config)

            embed = discord.Embed(
                title="Done",
                description="### メッセージの編集に成功しました\n反映には時間がかかる可能性がございます\n### 内容\nTitle: {}\nText: {}".format(
                    title, text),
                color=discord.Color.green()
            )

            await interaction.followup.send(embed=embed)
            return

    embed = discord.Embed(
        title="Error",
        description="You don't have permission to edit this message",
        color=discord.Color.red()
    )

    await interaction.followup.send(embed=embed)
    return


@tree.command(name="change_join_message_channel", description="参加時にメッセージを送信するチャンネルを変更します")
@commands.describe(channel="メッセージを送信するチャンネル")
async def change_join_message_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.defer()

    for role in interaction.user.roles:
        if role.permissions.administrator:
            config['Wisdom']['join_action_channel'] = channel.id
            save(config)

            embed = discord.Embed(
                title="Done",
                description="# 送信先チャンネルを変更しました\n{}".format(channel.jump_url),
                color=discord.Color.green()
            )

            await interaction.followup.send(embed=embed)
            return

    embed = discord.Embed(
        title="Error",
        description="You don't have permission to change",
        color=discord.Color.red()
    )

    await interaction.followup.send(embed=embed)

    return

# コマンドはこの前に
@tree.command(name="reload", description="botのコマンドを再読み込みします")
async def reload(interaction: discord.Interaction):
    await interaction.response.defer()

    for role in interaction.user.roles:
        if role.permissions.administrator:
            await tree.sync()

            embed = discord.Embed(
                title="Done Reload",
                description="コマンドの再読み込みに成功しました\n実装には時間がかかる可能性があります",
                color=discord.Color.green()
            )

            await interaction.followup.send(embed=embed)
            return

    embed = discord.Embed(
        title="Error",
        description="You don't have permission to reload",
        color=discord.Color.red()
    )

    await interaction.followup.send(embed=embed)

    return

# ここからメッセージとかもろもろの処理
@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name)
    await tree.sync()
    return

@bot.event
async def on_member_join(member: discord.Member):
    join_action_channel: int = int(config['Wisdom']['join_action_channel'])
    action_message = config['Wisdom']['message']
    embed = discord.Embed(
        title=action_message['join_message']['title'],
        description=action_message['join_message']['description'].replace('[user]', '<@{}>'.format(member.id)),
        color=discord.Color.green()
    )

    await bot.get_channel(join_action_channel).send(embed=embed)

    if member.bot:
        role_id: int = int(config['Wisdom']['bot_role'])
        role = member.guild.get_role(role_id)
        await member.add_roles(role)

        log_channel_id: int = int(action_message['other_log_channel'])
        log_channel = bot.get_channel(log_channel_id)

        embed = discord.Embed(
            title="Add role",
            description="<@{}>に<@&{}>を付与しました".format(member.id, role_id),
            color=discord.Color.green()
        )

        await log_channel.send(embed=embed)
    return

@bot.event
async def on_member_remove(member: discord.Member):
    left_action_channel: int = int(config['Wisdom']['left_action_channel'])
    action_message = config['Wisdom']['message']
    embed = discord.Embed(
        title=action_message['left_message']['title'],
        description=action_message['left_message']['description'].replace('[user]', '<@{}>'.format(member.id)),
        color=discord.Color.red()
    )

    await bot.get_channel(left_action_channel).send(embed=embed)
    return

bot.run(token)