import discord
from discord.ext import commands
from discord.ui import View, Select, Button, Modal, TextInput

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="$", intents=intents)

# 🎯 Modal pour entrer un nombre de messages à supprimer
class DeleteAmountModal(Modal, title="Combien de messages supprimer ?"):
    nombre = TextInput(label="Nombre de messages", placeholder="Ex : 10", required=True)

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.nombre.value)

            # ✅ Réponse immédiate pour éviter l'erreur 10062
            await interaction.response.defer(ephemeral=True)

            deleted = await self.channel.purge(limit=count)
            await interaction.followup.send(
                f"✅ {len(deleted)} messages supprimés dans {self.channel.mention}.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {e}", ephemeral=True)

# 🧩 View avec menu pour choisir un salon
class PurgeView(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx

        salons = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in ctx.guild.text_channels
        ]

        self.select = Select(
            placeholder="Choisir un salon...",
            options=salons,
            min_values=1,
            max_values=1
        )
        self.select.callback = self.choisir_salon
        self.add_item(self.select)

    async def choisir_salon(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Tu ne peux pas utiliser cette UI.", ephemeral=True)
            return

        salon_id = int(self.select.values[0])
        salon = self.ctx.guild.get_channel(salon_id)

        modal = DeleteAmountModal(channel=salon)
        await interaction.response.send_modal(modal)

# ✅ Commande principale
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge_ui(ctx):
    """Lance une interface pour supprimer des messages dans un salon au choix"""
    view = PurgeView(ctx)
    await ctx.send("🧹 Choisis un salon pour supprimer des messages :", view=view)


bot.run('MTM2Nzg3NjA5NTU4Nzc3ODYzMA.Gzzcag.e2RMdZhkDa7nwBpL52sIb7mgKVpTinS8mpIyU0')
