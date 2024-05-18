import os
import sqlite3
from game_stats import GameStats
from game_stats import PlayerStats
from game_stats import AggregatedPlayerStats

DB_NAME = f"{os.path.dirname(os.path.realpath(__file__))}/riichi-stats.db"

class DbInterface(object):
  """database interface class"""

  def __init__(self):
    self.conn = sqlite3.connect(DB_NAME)

  def __del__(self):
    self.conn.close()

  def init_db(self):
    """init tables in db, this should be called for a brand new db only"""
    cur = self.conn.cursor()
    cur.execute(f"""
      CREATE TABLE players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name INTEGER NOT NULL
      )
    """)
    cur.execute(f"""
      CREATE TABLE games (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date INTEGER NOT NULL, 

        east_player_name TEXT NOT NULL, 
        east_player_points INTEGER NOT NULL,  
        east_player_riichi INTEGER NOT NULL,
        east_player_agari INTEGER NOT NULL,
        east_player_deal_in INTEGER NOT NULL,

        south_player_name TEXT NOT NULL, 
        south_player_points INTEGER NOT NULL,  
        south_player_riichi INTEGER NOT NULL,
        south_player_agari INTEGER NOT NULL,
        south_player_deal_in INTEGER NOT NULL,

        west_player_name TEXT NOT NULL, 
        west_player_points INTEGER NOT NULL,  
        west_player_riichi INTEGER NOT NULL,
        west_player_agari INTEGER NOT NULL,
        west_player_deal_in INTEGER NOT NULL,

        north_player_name TEXT NOT NULL, 
        north_player_points INTEGER NOT NULL,  
        north_player_riichi INTEGER NOT NULL,
        north_player_agari INTEGER NOT NULL,
        north_player_deal_in INTEGER NOT NULL
      )
    """)
    self.conn.commit()

  def add_player(self, player_name):
    """add a new player"""
    if self.player_exists(player_name):
      return
    cur = self.conn.cursor()
    cur.execute(f"""
      INSERT INTO players (player_name) VALUES ('{player_name}')
    """)
    self.conn.commit()

  def player_exists(self, player_name):
    """weather a player exists in the db"""
    cur = self.conn.cursor()
    rst = cur.execute(f"""
      SELECT * FROM players WHERE player_name = '{player_name}'
    """)
    return rst.fetchone() != None

  def list_players(self):
    """list all players"""
    cur = self.conn.cursor()
    rst = cur.execute(f"""
      SELECT * FROM players
    """)
    return rst.fetchall()

  def record_game(self, game_stats):
    """record a game stats"""
    cur = self.conn.cursor()
    cur.execute(f"""
      INSERT INTO games
        ( date,

          east_player_name,
          east_player_points,
          east_player_riichi,
          east_player_agari,
          east_player_deal_in,

          south_player_name,
          south_player_points,
          south_player_riichi,
          south_player_agari,
          south_player_deal_in,

          west_player_name,
          west_player_points,
          west_player_riichi,
          west_player_agari,
          west_player_deal_in,

          north_player_name,
          north_player_points, 
          north_player_riichi,
          north_player_agari,
          north_player_deal_in
        ) VALUES
        (
          {game_stats.date},
          '{game_stats.east_player_stats.player_name}',
          {game_stats.east_player_stats.points},
          {game_stats.east_player_stats.riichi},
          {game_stats.east_player_stats.agari},
          {game_stats.east_player_stats.deal_in},

          '{game_stats.south_player_stats.player_name}',
          {game_stats.south_player_stats.points},
          {game_stats.south_player_stats.riichi},
          {game_stats.south_player_stats.agari},
          {game_stats.south_player_stats.deal_in},

          '{game_stats.west_player_stats.player_name}',
          {game_stats.west_player_stats.points},
          {game_stats.west_player_stats.riichi},
          {game_stats.west_player_stats.agari},
          {game_stats.west_player_stats.deal_in},

          '{game_stats.north_player_stats.player_name}',
          {game_stats.north_player_stats.points},
          {game_stats.north_player_stats.riichi},
          {game_stats.north_player_stats.agari},
          {game_stats.north_player_stats.deal_in}
        )
    """)
    self.conn.commit()

  def list_games(self, start_date, end_date, player_name=None):
    """list all games between given dates, and potentially for a given player"""
    cur = self.conn.cursor()
    player_filter = ""
    if player_name is not None:
      player_filter = f"""
        (east_player_name = "{player_name}")
        OR (south_player_name = "{player_name}")
        OR (west_player_name = "{player_name}")
        OR (north_player_name = "{player_name}")
      """
    rst = cur.execute(f"""
      SELECT 
        *
      FROM 
        games
      WHERE 
        {player_filter}
        date BETWEEN {start_date} AND {end_date}
    """)
    return rst.fetchall()

  def get_aggregated_stats(self, start_date, end_date, player_name=None):
    """get aggregated stats for all games between two given dates, and potenially for a given player"""


db = DbInterface()
db.init_db()

db.add_player("Ep")
db.add_player("Rodrick")
db.add_player("lailai")
db.add_player("Junhan")
players = db.list_players()
print(players)

game1 = GameStats(game_id=1,
                  date=20240517, 
                  east_player_stats=PlayerStats(
                      player_name='Ep',
                      points = 30000,
                      riichi = 3,
                      agari = 2,
                      deal_in = 1,
                    ),
                  south_player_stats=PlayerStats(
                      player_name='Junhan',
                      points = 23000,
                      riichi = 1,
                      agari = 3,
                      deal_in = 5,
                    ),
                  west_player_stats=PlayerStats(
                      player_name='lailai',
                      points = 47000,
                      riichi = 4,
                      agari = 2,
                      deal_in = 0,
                    ),
                  north_player_stats=PlayerStats(
                      player_name='Rodrick',
                      points = 10000,
                      riichi = 1,
                      agari = 0,
                      deal_in = 4,
                    ),
                  )

db.record_game(game1)
games = db.list_games(20240501, 20240601)
print(games)
