import subprocess
import discord
import asyncio
import configparser


cfg = configparser.ConfigParser()
cfg.read('auth.ini')


TOKEN = cfg.get('discord', 'token')
POLLING = {
    "command": cfg.get('polling', 'command'),
    "interval": float(cfg.get('polling', 'interval')),
    "channel": cfg.get('polling', 'channel'),
    "channel_refs": []
}
CLIENT = discord.Client()


def set_channel_refs():
    POLLING["channel_refs"] = []
    for guild in CLIENT.guilds:
        for channel in guild.channels:
            if str(channel) == POLLING["channel"]:
                POLLING["channel_refs"] += [channel]


async def poll_loop():
    await CLIENT.wait_until_ready()
    print(f"Logged in as { CLIENT.user.name }")
    set_channel_refs()

    while not CLIENT.is_closed():
        output = subprocess.run(
            POLLING["command"].split(),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        embed = discord.Embed(type="rich")

        embed.add_field(
            name="Output",
            value=str(output.stdout, "utf-8").strip() or "N/A",
            inline=False
        )
        if len(output.stderr) > 1:
            print("\nCommand failed")
            embed.title = "Error: command failed"
            embed.colour = 0xdc3545
            embed.add_field(
                name="Error message",
                value=str(output.stderr, "utf-8").strip() or "N/A",
                inline=False
            )
        else:
            print("\nCommand output:\n" + str(output.stdout, "utf-8"))
            embed.title = "Successfully ran command"
            embed.colour = 0x28a745

        for channel in POLLING["channel_refs"]:
            print(f"Told {channel.guild}")
            await channel.send(embed=embed)

        await asyncio.sleep(POLLING["interval"] * 60)


CLIENT.loop.create_task(poll_loop())
CLIENT.run(TOKEN)
