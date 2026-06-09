import asyncio
import secrets
import string

import discord
from discord import app_commands
from discord.ext import commands
import mysql.connector
from mysql.connector import Error as MySQLError
import redis

from utils.config import basicconfig


class LinkingSystemCog(commands.GroupCog, name="minecraft"):
    def __init__(self, bot):
        self.bot = bot
        self._schema_ready = False

    def redis_client(self):
        redis_config = basicconfig.REDIS
        return redis.Redis(
            host=redis_config.get("HOST") or "127.0.0.1",
            port=int(redis_config.get("PORT") or 6379),
            username=redis_config.get("USERNAME") or None,
            password=redis_config.get("PASSWORD") or None,
            db=int(redis_config.get("DB") or 0),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

    def mysql_connection(self):
        mysql_config = basicconfig.MYSQL
        return mysql.connector.connect(
            host=mysql_config.get("HOST") or "127.0.0.1",
            port=int(mysql_config.get("PORT") or 3306),
            user=mysql_config.get("USER") or None,
            password=mysql_config.get("PASSWORD") or None,
            database=mysql_config.get("DATABASE") or None,
            connection_timeout=5,
        )

    def ensure_schema(self):
        if self._schema_ready:
            return

        with self.mysql_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS linkcraft_links (
                        minecraft_uuid CHAR(36) NOT NULL PRIMARY KEY,
                        discord_user_id VARCHAR(32) NOT NULL UNIQUE,
                        linked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            connection.commit()

        self._schema_ready = True

    def get_link_by_discord_id(self, discord_user_id):
        self.ensure_schema()

        with self.mysql_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT minecraft_uuid, discord_user_id, linked_at
                    FROM linkcraft_links
                    WHERE discord_user_id = %s
                    LIMIT 1
                    """,
                    (str(discord_user_id),),
                )
                return cursor.fetchone()

    def delete_link_by_discord_id(self, discord_user_id):
        self.ensure_schema()

        with self.mysql_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM linkcraft_links WHERE discord_user_id = %s",
                    (str(discord_user_id),),
                )
                deleted_rows = cursor.rowcount
            connection.commit()
            return deleted_rows

    def create_link_code(self, discord_user_id):
        self.ensure_schema()

        client = self.redis_client()
        client.ping()

        linking_config = basicconfig.LINKING
        code_length = int(linking_config.get("CODE_LENGTH") or 6)
        ttl_seconds = int(linking_config.get("CODE_TTL_SECONDS") or 300)
        code_prefix = linking_config.get("CODE_PREFIX") or "linkcraft:code:"
        alphabet = string.ascii_uppercase + string.digits

        for _ in range(10):
            code = "".join(secrets.choice(alphabet) for _ in range(code_length))
            key = f"{code_prefix}{code}"
            if client.set(key, str(discord_user_id), ex=ttl_seconds, nx=True):
                return code, ttl_seconds

        raise RuntimeError("Could not create a unique verification code.")

    @app_commands.command(
        name="link",
        description="Generate a Minecraft account linking code.",
    )
    async def link(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        discord_user_id = str(interaction.user.id)

        try:
            existing_link = await asyncio.to_thread(
                self.get_link_by_discord_id,
                discord_user_id,
            )
            if existing_link:
                await interaction.followup.send(
                    "Your Discord account is already linked. Use `/minecraft unlink` before linking another Minecraft account.",
                    ephemeral=True,
                )
                return

            code, ttl_seconds = await asyncio.to_thread(
                self.create_link_code,
                discord_user_id,
            )
        except MySQLError:
            await interaction.followup.send(
                "The linking database is not available right now. Try again later.",
                ephemeral=True,
            )
            return
        except redis.RedisError:
            await interaction.followup.send(
                "The verification-code service is not available right now. Try again later.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"Log in to Minecraft and run `/link {code}` within {ttl_seconds // 60} minute(s).",
            ephemeral=True,
        )

    @app_commands.command(
        name="unlink",
        description="Unlink your Minecraft account from this Discord account.",
    )
    async def unlink(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        discord_user_id = str(interaction.user.id)

        try:
            deleted_rows = await asyncio.to_thread(
                self.delete_link_by_discord_id,
                discord_user_id,
            )
        except MySQLError:
            await interaction.followup.send(
                "The linking database is not available right now. Try again later.",
                ephemeral=True,
            )
            return

        if deleted_rows:
            await interaction.followup.send(
                "Your Minecraft account has been unlinked.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "Your Discord account is not linked to a Minecraft account.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(LinkingSystemCog(bot))
