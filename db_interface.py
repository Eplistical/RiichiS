import os
import sqlite3
from typing import Optional
from game_stats import GameStats
from game_stats import PlayerStats

DB_NAME: str = f"{os.path.dirname(os.path.realpath(__file__))}/riichi-stats.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DbInterface(object):
  """database interface class"""

  def __init__(self):
    self.conn = sqlite3.connect(DB_NAME)
    self.conn.row_factory = dict_factory

  def __del__(self):
    self.conn.close()

  def init_db(self) -> None:
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
        east_player_riichi INTEGER,
        east_player_agari INTEGER,
        east_player_deal_in INTEGER,

        south_player_name TEXT NOT NULL, 
        south_player_points INTEGER NOT NULL,  
        south_player_riichi INTEGER,
        south_player_agari INTEGER,
        south_player_deal_in INTEGER,

        west_player_name TEXT NOT NULL, 
        west_player_points INTEGER NOT NULL,  
        west_player_riichi INTEGER,
        west_player_agari INTEGER,
        west_player_deal_in INTEGER,

        north_player_name TEXT NOT NULL, 
        north_player_points INTEGER NOT NULL,  
        north_player_riichi INTEGER,
        north_player_agari INTEGER,
        north_player_deal_in INTEGER
      )
    """)
    self.conn.commit()

  def add_player(self, player_name: str) -> None:
    """add a new player"""
    if self.player_exists(player_name):
      return
    cur = self.conn.cursor()
    cur.execute(f"""
      INSERT INTO players (player_name) VALUES ('{player_name}')
    """)
    self.conn.commit()

  def player_exists(self, player_name: str) -> None:
    """weather a player exists in the db"""
    cur = self.conn.cursor()
    rst = cur.execute(f"""
      SELECT * FROM players WHERE player_name = '{player_name}'
    """)
    return rst.fetchone() != None

  def list_players(self) -> list[str]:
    """list all players"""
    cur = self.conn.cursor()
    rst = cur.execute(f"""
      SELECT * FROM players
    """)
    return rst.fetchall()

  def record_game(self, game_stats: GameStats) -> None:
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

  def list_games(self, start_date: int, end_date: int, player_name: Optional[str]=None) -> list[GameStats]:
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
      ORDER BY
        game_id ASC
    """)
    games = []
    for data in rst.fetchall():
      game = GameStats(
        game_id=data['game_id'],
        date=data['date'],
        east_player_stats=PlayerStats(
          player_name=data['east_player_name'],
          points=data['east_player_points'],
          riichi=data['east_player_riichi'],
          agari=data['east_player_agari'],
          deal_in=data['east_player_deal_in'],
        ),
        south_player_stats=PlayerStats(
          player_name=data['south_player_name'],
          points=data['south_player_points'],
          riichi=data['south_player_riichi'],
          agari=data['south_player_agari'],
          deal_in=data['south_player_deal_in'],
        ),
        west_player_stats=PlayerStats(
          player_name=data['west_player_name'],
          points=data['west_player_points'],
          riichi=data['west_player_riichi'],
          agari=data['west_player_agari'],
          deal_in=data['west_player_deal_in'],
        ),
        north_player_stats=PlayerStats(
          player_name=data['north_player_name'],
          points=data['north_player_points'],
          riichi=data['north_player_riichi'],
          agari=data['north_player_agari'],
          deal_in=data['north_player_deal_in'],
        )
      )
      games.append(game)
    return games

