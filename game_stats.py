from dataclasses import dataclass
from typing import Optional

@dataclass
class PlayerStats:
  player_name: str # player name
  points: int # end game points
  riichi: Optional[int] # riichi count
  agari: Optional[int]  # agari count
  deal_in: Optional[int] # deal-in count

@dataclass
class GameStats:
  game_id: Optional[int]
  date: int # date of the game, YYYYMMDD format
  east_player_stats: PlayerStats
  south_player_stats: PlayerStats
  west_player_stats: PlayerStats
  north_player_stats: PlayerStats

@dataclass
class AggregatedPlayerStats:
  player_name: str
  start_date: int
  end_date: int
  games_count: int
  place_count_map: dict[int, int]
  top_k_count_map: dict[int, int]
  rank_sum: int
  max_points: Optional[int]
  points_sum: int
  points_sum_with_uma: int
  riichi_sum: int
  agari_sum: int
  deal_in_sum: int