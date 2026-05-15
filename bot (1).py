import discord
from discord import app_commands
from discord.ui import Modal, TextInput
import aiohttp
import os

# Token et webhook lus depuis les variables d'environnement Railway
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_AVIS = os.environ["WEBHOOK_AVIS"]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


class AvisModal(Modal, title="Laisser un avis Eclipse Official"):
    produit = TextInput(
        label="Produit achete",
        placeholder="Ex: One Click, Unlock All, Astherial, Elysian",
        required=True,
        max_length=50
    )
    note = TextInput(
        label="Note sur 5",
        placeholder="Ex: 5/5 ou 4/5",
        required=True,
        max_length=10
    )
    avis = TextInput(
        label="Ton avis",
        placeholder="Dis ce que tu penses du produit...",
        required=True,
        max_length=500,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = {
            "embeds": [{
                "title": "NOUVEL AVIS CLIENT",
                "color": 0xf59e0b,
                "fields": [
                    {"name": "Pseudo", "value": str(interaction.user), "inline": True},
                    {"name": "Produit", "value": self.produit.value, "inline": True},
                    {"name": "Note", "value": self.note.value, "inline": True},
                    {"name": "Avis", "value": self.avis.value, "inline": False},
                ],
                "footer": {"text": "Eclipse Official"},
                "timestamp": discord.utils.utcnow().isoformat()
            }]
        }
        async with aiohttp.ClientSession() as session:
            await session.post(WEBHOOK_AVIS, json=embed)
        await interaction.followup.send("Merci pour ton avis !", ephemeral=True)


class AvisBouton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=86400)

    @discord.ui.button(label="Laisser mon avis", style=discord.ButtonStyle.success)
    async def laisser_avis(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AvisModal())
        button.disabled = True
        await interaction.message.edit(view=self)


@tree.command(name="avis", description="Demander un avis a un client")
@app_commands.describe(membre="Le client a qui demander un avis")
async def avis_cmd(interaction: discord.Interaction, membre: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Permission refusee.", ephemeral=True)
        return
    await interaction.response.send_message(f"Demande envoyee a {membre.mention} !", ephemeral=True)
    try:
        await membre.send(
            "Bonjour ! Eclipse Official t'invite a laisser un avis.\nClique ci-dessous :",
            view=AvisBouton()
        )
    except discord.Forbidden:
        await interaction.followup.send(f"Impossible d'envoyer un DM (DMs fermes).", ephemeral=True)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot connecte : {client.user}")


client.run(BOT_TOKEN)
