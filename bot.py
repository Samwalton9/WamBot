import discord
import asyncio
import matplotlib.pyplot as plt

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as', client.user.name)
    print('\nLogged in to the following servers:')
    for server in client.servers:
        print(server.name)
    print('-----')

@client.event
async def on_message(message):
    is_command = message.content.startswith('$')
    if is_command:
        message_author = message.author
        author_roles = [str(i) for i in message_author.roles]
        if 'Moderators' in author_roles:
            await parse_command(message.content, message.channel)
        else:
            error_message = "Error: You must be a moderator to do that"
            await client.send_message(message.channel, content=error_message)

async def parse_command(command_string, command_channel):

    command_list = {
        'modlog': modlog_history
    }

    split_command = command_string[1:].split(" ")
    primary_command = split_command[0]

    args = split_command[1:]
    if primary_command in command_list:
        try:
            result = await command_list[primary_command](command_channel, *args)
        except TypeError as e:
            result = "Error: Wrong number of arguments given"
    else:
        result = "Error: That command doesn't exist"

    if result:
        await client.send_message(command_channel, content=result)

async def modlog_history(command_channel, message_limit):

    try:
        limit_int = int(message_limit)
    except ValueError:
        error_message = "Error: Please use a number."
        return error_message

    collecting_message = await client.send_message(
        command_channel, content="Collecting data...")

    #log_channel = client.get_channel('382550498533703680')  # bot-testing
    log_channel = client.get_channel('302525012143898631')  # mod-log

    message_log = client.logs_from(log_channel, limit=limit_int)
    hours_log = []

    async for historical_message in message_log:
        if historical_message.content.startswith('!'):
            message_hour = historical_message.timestamp.hour
            hours_log.append(message_hour)

    public_log = await hourly_activity()

    f = plt.figure()

    plot_args = {'bins':24, 'range':(0,24), 'normed':True, 'histtype':'step'}

    plt.hist(hours_log, color='black', **plot_args)
    plt.hist(public_log, color='red', **plot_args)

    x1, x2, y1, y2 = plt.axis()
    plt.axis((0,24,y1,y2))
    plt.xlabel('Hour (UTC)')
    plt.ylabel('Fraction of all messages')
    plt.xticks(range(0,25))

    f.set_size_inches(10,5)
    f.savefig('graphs/message_log', dpi=300)
    print("Done analysing messages.")

    await client.edit_message(collecting_message,
                              collecting_message.content + " Done.")
    
    await client.send_file(command_channel,
                           'graphs/message_log.png',
                           filename='Modlog history.png')

async def hourly_activity():
    all_channels = client.get_all_channels()
    public_channels = [289466476187090944, 300462993995726848,
                       289468705878966277,
                       294240895937675273, 289502676675198976]

    lfg_channels = [channel.id for channel in all_channels
                    if channel.server.name == '/r/PUBATTLEGROUNDS'
                    and ('looking-for-group' in channel.name
                    or 'na-' in channel.name
                    or 'eu-' in channel.name)]

    public_pubg_channels = public_channels + lfg_channels
    
    hours_log = []
    for channel in public_pubg_channels:

        log_channel = client.get_channel(str(channel))
        print("Counting messages in ", log_channel)

        message_log = client.logs_from(log_channel, limit=1000)

        async for historical_message in message_log:
            message_hour = historical_message.timestamp.hour
            hours_log.append(message_hour)

    return hours_log

with open('bot_token') as f:
    token = f.readline().strip()
client.run(token)