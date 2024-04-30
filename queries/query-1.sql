--SQLite
DROP VIEW IF EXISTS cummlative_goals;
CREATE VIEW cummlative_goals as
SELECT 
  start_time,
  id, 
  home_team_id,
  away_team_id,
  home_goals,
  away_goals,
  home_goals - away_goals as goal_diff
  
  -- Home Team
  (
    SELECT SUM(home_goals) 
    FROM Fixture 
      WHERE home_team_id = f.home_team_id 
      AND start_time < f.start_time
  ) AS H_GF_AT_HOME,
  
  (
    SELECT SUM(away_goals) 
    FROM Fixture 
      WHERE home_team_id = f.home_team_id 
      AND start_time < f.start_time
  ) AS H_GA_AT_HOME,
  
  (
    SELECT SUM(home_goals) 
    FROM Fixture 
    WHERE away_team_id = f.home_team_id 
    AND start_time < f.start_time
  ) AS H_GA_ON_THE_ROAD,
  
  (
    SELECT SUM(away_goals) 
    FROM Fixture 
    WHERE away_team_id = f.home_team_id 
    AND start_time < f.start_time
  ) AS H_GF_ON_THE_ROAD,

  (
    SELECT SUM(home_goals) 
    FROM Fixture 
      WHERE home_team_id = f.away_team_id 
      AND start_time < f.start_time
  ) AS A_GF_AT_HOME,
  
  (
    SELECT SUM(away_goals) 
    FROM Fixture 
      WHERE home_team_id = f.away_team_id 
      AND start_time < f.start_time
  ) AS A_GA_AT_HOME,
  
  (
    SELECT SUM(home_goals) 
    FROM Fixture 
    WHERE away_team_id = f.away_team_id 
    AND start_time < f.start_time
  ) AS A_GA_ON_THE_ROAD,
  
  (
    SELECT SUM(away_goals) 
    FROM Fixture 
    WHERE away_team_id = f.away_team_id 
    AND start_time < f.start_time
  ) AS A_GF_ON_THE_ROAD
FROM fixture as f
ORDER BY home_team_id;

CREATE grouped_stats as 
SELECT
  team_id,
  fixture_id,
  position,
  AVG((passing_accuracy*100.0 / total_passes)) AS average_passing_percentage, 
  AVG((duels_won*100.0 / total_duels)) AS average_duels_won_percentage, 
  AVG(rating) as average_rating,
  SUM(total_passes) as aggregate_passes,
  SUM(key_passes) as aggregate_key_passes,
  SUM(interceptions) AS total_interceptions,
  SUM(tackles) AS total_tackles,
  SUM(blocks) AS total_blocks,
  AVG(successful_dribbles*100.0 / dribble_attempts) AS dribble_success_percentage

FROM statistic
WHERE substitute = 0
GROUP BY fixture_id, team_id, position
ORDER BY fixture_id, team_id DESC;

DROP VIEW IF EXISTS defener_stats;
CREATE VIEW defender_stats as
SELECT * FROM grouped_stats as gs
WHERE position = 'D';

DROP VIEW IF EXISTS midfield_stats;
CREATE VIEW midfield_stats as
SELECT * FROM grouped_stats as gs
WHERE position = 'M';

DROP VIEW IF EXISTS forward_stats
CREATE VIEW forward_stats as
SELECT * FROM grouped_stats as gs
WHERE position = 'F';

SELECT * FROM forward_stats;
SELECT * FROM midfield_stats;
SELECT * FROM defender_stats;

SELECT *, 
  AVG(average_passing_percentage) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_average_passing_percentage,
  AVG(average_duels_won_percentage) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_duels_won_percentage,
  AVG(average_rating) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_rating,
  AVG(aggregate_passes) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_average_total_passes,
  AVG(aggregate_key_passes) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_average_key_passes,
  AVG(total_interceptions) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_average_interceptions,
  AVG(total_tackles) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_average_total_tackles,
  AVG(total_blocks) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_average_total_blocks,
  AVG(dribble_success_percentage) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS cumulative_average_dribble_success_percentage
FROM forward_stats;

CREATE VIEW denorm_stats as
SELECT 
  COUNT(
  
  cg.*,
  -- HOME
  -- FORWARDS
  AVG(hfs.average_passing_percentage) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_passing_percentage,
  AVG(hfs.average_duels_won_percentage) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_duels_won_percentage,
  AVG(hfs.average_rating) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_rating,
  AVG(hfs.aggregate_passes) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_total_passes,
  AVG(hfs.aggregate_key_passes) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_key_passes,
  AVG(hfs.total_interceptions) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_interceptions,
  AVG(hfs.total_tackles) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_total_tackles,
  AVG(hfs.total_blocks) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_total_blocks,
  AVG(hfs.dribble_success_percentage) OVER(PARTITION BY hfs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_dribble_success_percentage,
  
  -- MIDFIELDERS
  AVG(hms.average_passing_percentage) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_passing_percentage,
  AVG(hms.average_duels_won_percentage) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_duels_won_percentage,
  AVG(hms.average_rating) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_rating,
  AVG(hms.aggregate_passes) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_total_passes,
  AVG(hms.aggregate_key_passes) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_key_passes,
  AVG(hms.total_interceptions) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_interceptions,
  AVG(hms.total_tackles) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_total_tackles,
  AVG(hms.total_blocks) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_total_blocks,
  AVG(hms.dribble_success_percentage) OVER(PARTITION BY hms.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_dribble_success_percentage,

  -- DEFENDERS
  AVG(hds.average_passing_percentage) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_passing_percentage,
  AVG(hds.average_duels_won_percentage) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_duels_won_percentage,
  AVG(hds.average_rating) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_rating,
  AVG(hds.aggregate_passes) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_total_passes,
  AVG(hds.aggregate_key_passes) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_key_passes,
  AVG(hds.total_interceptions) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_interceptions,
  AVG(hds.total_tackles) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_total_tackles,
  AVG(hds.total_blocks) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_total_blocks,
  AVG(hds.dribble_success_percentage) OVER(PARTITION BY hds.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_dribble_success_percentage,
  
  -- Away 
  -- FORWARDS
  AVG(afs.average_passing_percentage) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_passing_percentage,
  AVG(afs.average_duels_won_percentage) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_duels_won_percentage,
  AVG(afs.average_rating) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_rating,
  AVG(afs.aggregate_passes) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_total_passes,
  AVG(afs.aggregate_key_passes) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_key_passes,
  AVG(afs.total_interceptions) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_interceptions,
  AVG(afs.total_tackles) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_total_tackles,
  AVG(afs.total_blocks) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_total_blocks,
  AVG(afs.dribble_success_percentage) OVER(PARTITION BY afs.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_dribble_success_percentage,

  -- MIDFIELDERS
  AVG(ams.average_passing_percentage) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_passing_percentage,
  AVG(ams.average_duels_won_percentage) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_duels_won_percentage,
  AVG(ams.average_rating) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_rating,
  AVG(ams.aggregate_passes) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_total_passes,
  AVG(ams.aggregate_key_passes) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_key_passes,
  AVG(ams.total_interceptions) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_interceptions,
  AVG(ams.total_tackles) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_total_tackles,
  AVG(ams.total_blocks) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_total_blocks,
  AVG(ams.dribble_success_percentage) OVER(PARTITION BY ams.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_dribble_success_percentage,

  
  -- DEFENDERS
  AVG(ads.average_passing_percentage) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_passing_percentage,
  AVG(ads.average_duels_won_percentage) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_duels_won_percentage,
  AVG(ads.average_rating) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_rating,
  AVG(ads.aggregate_passes) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_total_passes,
  AVG(ads.aggregate_key_passes) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_key_passes,
  AVG(ads.total_interceptions) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_interceptions,
  AVG(ads.total_tackles) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_total_tackles,
  AVG(ads.total_blocks) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_total_blocks,
  AVG(ads.dribble_success_percentage) OVER(PARTITION BY ads.team_id ORDER BY cg.start_time ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_dribble_success_percentage
  
  
FROM cummlative_goals as cg

LEFT JOIN forward_stats as hfs
ON cg.id = hfs.fixture_id AND cg.home_team_id=hfs.team_id
LEFT JOIN forward_stats as afs
ON cg.id = afs.fixture_id AND cg.away_team_id=afs.team_id

LEFT JOIN defender_stats as hds
ON cg.id = hds.fixture_id AND cg.home_team_id = hds.team_id
LEFT JOIN defender_stats as ads
ON cg.id = ads.fixture_id AND cg.away_team_id = ads.team_id

LEFT JOIN midfield_stats as hms
ON cg.id = hms.fixture_id AND cg.home_team_id = hms.team_id
LEFT JOIN midfield_stats as ams
ON cg.id = ams.fixture_id AND cg.away_team_id = ams.team_id

ORDER BY start_time;


SELECT * FROM denorm_stats;

SELECT * FROM cummlative_goals;


-- GROUP BY team_id
-- ORDER BY AVG(passing_accuracy) DESC;

-- DELETE FROM statistic;

