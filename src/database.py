import sqlite3
import os
from discord.ext.commands import Bot

DB_DIR = os.path.join("db")
DB_PATH = os.path.join("db", "database.db")

def db_init():
    os.makedirs(DB_DIR, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS guilds (
                            guild_id TEXT PRIMARY KEY,
                            counting_channel_id TEXT
                        )
                    """)
        
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT NOT NULL,
                        guild_id TEXT NOT NULL,
                        channel_id TEXT NOT NULL,
                        counted_numbers INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id, guild_id, channel_id),
                        FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
                    )
                    """)
        
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS channels (
                            channel_id TEXT PRIMARY KEY,
                            guild_id TEXT,
                            current_number INTEGER DEFAULT 1,
                            last_user TEXT NOT NULL DEFAULT ''
                        )
                    """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    
    
    
def insert_guild(guild_id, channel_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   INSERT OR REPLACE INTO guilds (guild_id, counting_channel_id) VALUES (?, ?)
                   """, (guild_id, channel_id))
    
    conn.commit()
    conn.close()

def get_current_number(channel_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT current_number FROM channels WHERE channel_id = ?
                   """, (channel_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None
    
def update_channel(channel_id, next_num, user_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   INSERT OR REPLACE INTO channels (channel_id, guild_id, current_number, last_user)
                   VALUES (?, (SELECT guild_id FROM guilds where counting_channel_id = ?), ?, ?)
                   """, (channel_id, channel_id, next_num, user_id))
    
    conn.commit()
    conn.close()
    
def update_user_count(user_id, guild_id, channel_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   INSERT INTO users (user_id, guild_id, channel_id, counted_numbers) VALUES (?, ?, ?,1)
                   ON CONFLICT(user_id, guild_id, channel_id) DO UPDATE SET counted_numbers = counted_numbers + 1
                   """, (user_id, guild_id, channel_id))
    
    conn.commit()
    conn.close()
    
def get_leaderboard(guild_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT user_id, SUM(counted_numbers) AS total FROM users WHERE guild_id = ? ORDER BY counted_numbers DESC
                   """, (guild_id,))
    
    result = cursor.fetchall()
    conn.close()
    
    return result

def validate_channels(bot: Bot):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT channel_id, guild_id FROM channels
                   """)
    channels = cursor.fetchall()
    
    for channel_id, guild_id in channels:
        try:
            guild = bot.get_guild(int(guild_id))
            if not guild or not guild.get_channel(int(channel_id)):
                cursor.execute("""
                               DELETE FROM channels WHERE channel_id = ?
                               """,(channel_id,))
                cursor.execute("""
                               DELETE FROM guilds WHERE counting_channel_id = ?
                               """,(channel_id,))
                cursor.execute("""
                               DELETE FROM users WHERE channel_id = ?
                               """,(channel_id,))
        except Exception as e:
            print(f"Channel validation error on channel ID {channel_id}: {e}")
    
    conn.commit()
    conn.close()
    
def delete_channel(channel_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   DELETE FROM channels WHERE channel_id = ?
                   """,(channel_id,))
    
    cursor.execute("""
                   DELETE FROM guilds WHERE counting_channel_id = ? 
                   """,(channel_id,))
    
    cursor.execute("""
                   DELETE FROM users WHERE channel_id = ?
                   """,(channel_id,))
    
    conn.commit()
    conn.close()
    
def check_count_channel(channel_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT channel_id FROM channels WHERE channel_id = ?
                   """,(channel_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result

def get_last_user(channel_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT last_user FROM channels WHERE channel_id = ?
                   """,(channel_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0]