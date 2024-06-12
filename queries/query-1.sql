--SQLite
DROP VIEW IF EXISTS annotated_fixture;
CREATE VIEW annotated_fixture as 
SELECT 
  start_time,
  fixture.id, 
  season,
  home_team_id,
  away_team_id,
  home_team.name as home_name,
  away_team.name as away_name,
  away_team_id,
  home_goals,
  away_goals,
  home_goals > away_goals as home_win,
  away_goals > home_goals as away_win,
  home_goals = away_goals as is_draw
FROM fixture
LEFT JOIN team as home_team
ON home_team.id = fixture.home_team_id
LEFT JOIN team as away_team
ON away_team.id = fixture.away_team_id;
SELECT * FROM annotated_fixture;


SELECT * FROM statistic;




DROP VIEW IF EXISTS cummulative_goals;
CREATE VIEW cummulative_goals as
SELECT 
  start_time,
  id, 
  home_name,
  away_name,
  home_goals,
  away_goals,
  home_win,
  away_win,
  is_draw,
  
  -- Cummulative wins losses and draws for HOME TEAM
  SUM(CASE WHEN f.home_team_id = home_team_id THEN home_win ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_WINS_AT_HOME,

  SUM(CASE WHEN home_team_id = f.home_team_id THEN away_win ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_LOSSES_AT_HOME,
  
  SUM(CASE WHEN home_team_id = f.home_team_id THEN is_draw ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_DRAWS_AT_HOME,
  
  SUM(CASE WHEN away_team_id = f.home_team_id THEN CAST(away_win AS INT) ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_WINS_ON_THE_ROAD,
  
  SUM(CASE WHEN away_team_id = f.home_team_id THEN home_win ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_LOSSES_ON_THE_ROAD,
  
  SUM(CASE WHEN away_team_id = f.home_team_id THEN is_draw ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_DRAWS_ON_THE_ROAD,
  
  -- Cummulative wins losses and draws for AWAY TEAM
  SUM(CASE WHEN home_team_id = f.away_team_id THEN away_win ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_WINS_AT_HOME,

  SUM(CASE WHEN home_team_id = f.away_team_id THEN home_win ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_LOSSES_AT_HOME,
  
  SUM(CASE WHEN home_team_id = f.away_team_id THEN is_draw ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_DRAWS_AT_HOME,
  
  SUM(CASE WHEN away_team_id = f.away_team_id THEN away_win ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_WINS_ON_THE_ROAD,
  
  SUM(CASE WHEN away_team_id = f.away_team_id THEN home_win ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_LOSSES_ON_THE_ROAD,
  
  SUM(CASE WHEN away_team_id = f.away_team_id THEN is_draw ELSE 0 END) 
  OVER (PARTITION BY home_team_id ORDER BY start_time 
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_DRAWS_ON_THE_ROAD,

  -- Cummulative goals home team
  SUM(CASE WHEN home_team_id = f.home_team_id THEN home_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_GF_AT_HOME,
  
  SUM(CASE WHEN home_team_id = f.home_team_id THEN away_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_GA_AT_HOME,
  
  SUM(CASE WHEN away_team_id = f.home_team_id THEN home_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_GA_ON_THE_ROAD,
  SUM(CASE WHEN away_team_id = f.home_team_id THEN away_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS H_GF_ON_THE_ROAD,
  
  -- Cummlative goals away team
  SUM(CASE WHEN home_team_id = f.away_team_id THEN home_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_GF_AT_HOME,
  
  SUM(CASE WHEN home_team_id = f.away_team_id THEN away_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_GA_AT_HOME,
  
  SUM(CASE WHEN away_team_id = f.away_team_id THEN home_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_GA_ON_THE_ROAD,
  
  SUM(CASE WHEN away_team_id = f.away_team_id THEN away_goals ELSE 0 END)
  OVER (PARTITION BY home_team_id ORDER BY start_time
        ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS A_GF_ON_THE_ROAD

FROM annotated_fixture as f;


SELECT * FROM cummulative_goals;

-- SANITY CHECK
SELECT start_time, home_team_id, away_team_id, home_goals, away_goals, H_WINS_AT_HOME, H_LOSSES_AT_HOME, H_DRAWS_AT_HOME FROM cummulative_goals
WHERE home_team_id=33
ORDER BY start_time;

DROP VIEW IF EXISTS grouped_stats;
CREATE VIEW grouped_stats as 
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

DROP VIEW IF EXISTS defender_stats;
CREATE VIEW defender_stats as
SELECT * FROM grouped_stats as gs
WHERE position = 'D';

DROP VIEW IF EXISTS midfield_stats;
CREATE VIEW midfield_stats as
SELECT * FROM grouped_stats as gs
WHERE position = 'M';

DROP VIEW IF EXISTS forward_stats;
CREATE VIEW forward_stats as
SELECT * FROM grouped_stats as gs
WHERE position = 'F';

SELECT * FROM forward_stats;
SELECT * FROM midfield_stats;
SELECT * FROM defender_stats;



-- SIMPLIFIED:
SELECT 
  start_time,
  home_name,
  away_name,
  home_win,
  away_win,
  is_draw,
  SUM(CASE WHEN away_team_id = f.home_team_id THEN away_win ELSE 0 END) 
    OVER (PARTITION BY away_team_id ORDER BY start_time 
          ROWS BETWEEN 19 PRECEDING AND 1 PRECEDING) AS H_WINS_ON_THE_ROAD

FROM annotated_fixture as f
ORDER BY start_time;


-- WINDOW Function Example
SELECT *, 
  AVG(average_passing_percentage) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_average_passing_percentage,
  AVG(average_duels_won_percentage) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_duels_won_percentage,
  AVG(average_rating) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_rating,
  AVG(aggregate_passes) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_average_total_passes,
  AVG(aggregate_key_passes) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_average_key_passes,
  AVG(total_interceptions) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_average_interceptions,
  AVG(total_tackles) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_average_total_tackles,
  AVG(total_blocks) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_average_total_blocks,
  AVG(dribble_success_percentage) OVER(PARTITION BY team_id ORDER BY start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS cumulative_average_dribble_success_percentage
FROM forward_stats;


DROP VIEW IF EXISTS denorm_stats;
CREATE VIEW denorm_stats as
SELECT 
  
  af.*,
  -- FORWARDS
  AVG(hfs.average_passing_percentage) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_passing_percentage,
  AVG(hfs.average_duels_won_percentage) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_duels_won_percentage,
  AVG(hfs.average_rating) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_rating,
  AVG(hfs.aggregate_passes) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_total_passes,
  AVG(hfs.aggregate_key_passes) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_key_passes,
  AVG(hfs.total_interceptions) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_interceptions,
  AVG(hfs.total_tackles) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_total_tackles,
  AVG(hfs.total_blocks) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_total_blocks,
  AVG(hfs.dribble_success_percentage) OVER(PARTITION BY hfs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_forwards_cumulative_average_dribble_success_percentage,
  
  -- MIDFIELDERS
  AVG(hms.average_passing_percentage) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_passing_percentage,
  AVG(hms.average_duels_won_percentage) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_duels_won_percentage,
  AVG(hms.average_rating) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_rating,
  AVG(hms.aggregate_passes) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_total_passes,
  AVG(hms.aggregate_key_passes) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_key_passes,
  AVG(hms.total_interceptions) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_interceptions,
  AVG(hms.total_tackles) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_total_tackles,
  AVG(hms.total_blocks) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_total_blocks,
  AVG(hms.dribble_success_percentage) OVER(PARTITION BY hms.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_midfielders_cumulative_average_dribble_success_percentage,

  -- DEFENDERS
  AVG(hds.average_passing_percentage) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_passing_percentage,
  AVG(hds.average_duels_won_percentage) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_duels_won_percentage,
  AVG(hds.average_rating) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_rating,
  AVG(hds.aggregate_passes) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_total_passes,
  AVG(hds.aggregate_key_passes) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_key_passes,
  AVG(hds.total_interceptions) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_interceptions,
  AVG(hds.total_tackles) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_total_tackles,
  AVG(hds.total_blocks) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_total_blocks,
  AVG(hds.dribble_success_percentage) OVER(PARTITION BY hds.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS home_defenders_cumulative_average_dribble_success_percentage,
  
  -- Away 
  -- FORWARDS
  AVG(afs.average_passing_percentage) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_passing_percentage,
  AVG(afs.average_duels_won_percentage) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_duels_won_percentage,
  AVG(afs.average_rating) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_rating,
  AVG(afs.aggregate_passes) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_total_passes,
  AVG(afs.aggregate_key_passes) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_key_passes,
  AVG(afs.total_interceptions) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_interceptions,
  AVG(afs.total_tackles) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_total_tackles,
  AVG(afs.total_blocks) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_total_blocks,
  AVG(afs.dribble_success_percentage) OVER(PARTITION BY afs.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_forwards_cumulative_average_dribble_success_percentage,

  -- MIDFIELDERS
  AVG(ams.average_passing_percentage) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_passing_percentage,
  AVG(ams.average_duels_won_percentage) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_duels_won_percentage,
  AVG(ams.average_rating) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_rating,
  AVG(ams.aggregate_passes) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_total_passes,
  AVG(ams.aggregate_key_passes) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_key_passes,
  AVG(ams.total_interceptions) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_interceptions,
  AVG(ams.total_tackles) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_total_tackles,
  AVG(ams.total_blocks) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_total_blocks,
  AVG(ams.dribble_success_percentage) OVER(PARTITION BY ams.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_midfielders_cumulative_average_dribble_success_percentage,

  
  -- DEFENDERS
  AVG(ads.average_passing_percentage) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_passing_percentage,
  AVG(ads.average_duels_won_percentage) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_duels_won_percentage,
  AVG(ads.average_rating) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_rating,
  AVG(ads.aggregate_passes) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_total_passes,
  AVG(ads.aggregate_key_passes) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_key_passes,
  AVG(ads.total_interceptions) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_interceptions,
  AVG(ads.total_tackles) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_total_tackles,
  AVG(ads.total_blocks) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_total_blocks,
  AVG(ads.dribble_success_percentage) OVER(PARTITION BY ads.team_id ORDER BY af.start_time ROWS BETWEEN 38 PRECEDING AND 1 PRECEDING) AS away_defenders_cumulative_average_dribble_success_percentage
  
  
FROM annotated_fixture as af

LEFT JOIN forward_stats as hfs
ON af.id = hfs.fixture_id AND af.home_team_id=hfs.team_id
LEFT JOIN forward_stats as afs
ON af.id = afs.fixture_id AND af.away_team_id=afs.team_id

LEFT JOIN defender_stats as hds
ON af.id = hds.fixture_id AND af.home_team_id = hds.team_id
LEFT JOIN defender_stats as ads
ON af.id = ads.fixture_id AND af.away_team_id = ads.team_id

LEFT JOIN midfield_stats as hms
ON af.id = hms.fixture_id AND af.home_team_id = hms.team_id
LEFT JOIN midfield_stats as ams
ON af.id = ams.fixture_id AND af.away_team_id = ams.team_id

ORDER BY start_time;

-- FINAL SANITY CHECK
SELECT * FROM denorm_stats;
SELECT * FROM cummulative_goals;



SELECT * FROM fixture WHERE season = 2020;
SELECT * FROM statistic WHERE fixture_id = 710556;