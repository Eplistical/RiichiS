from dataclasses import dataclass

@dataclass
class PlayerStats:
  player_name: str # player name
  points: int # end game points
  riichi: int # riichi count
  agari: int  # agari count
  deal_in: int # deal-in count

@dataclass
class GameStats:
  game_id: int
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
  first_place_count: int
  second_place_count: int
  third_place_count: int
  fourth_place: int
  avg_rank: float
  top_rate: float # percentage of 1st place
  top2_rate: float # percentage of 1st&2nd places
  fourth_avoidance_rate: float # percentage of 1st&2nd&3rd places
  max_points: int
  avg_points: float
