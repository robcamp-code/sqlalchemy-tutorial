-- SQLite
SELECT 
  start_time, 
  home_team_id,
  away_team_id,
  home_goals,
  away_goals, 
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
  
    
        
 FROM Fixture AS f
 ORDER BY home_team_id, start_time;