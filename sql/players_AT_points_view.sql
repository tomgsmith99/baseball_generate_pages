
########################################################
# players_max_points_view

SELECT
    `players_all_time`.`player_id`,
    MAX(`players_all_time`.`points`) AS most_points
FROM `baseball`.`players_all_time`
GROUP BY `baseball`.`players_all_time`.`player_id`


########################################################
# players_best_year

SELECT 
    `players_max_points_view`.`player_id`,
    `players_max_points_view`.`most_points`,
    MAX(`players_all_time`.`season`) AS season
FROM
    `players_max_points_view`, `players_all_time`
WHERE
    `players_max_points_view`.`most_points` = `players_all_time`.`points`
    AND
    `players_max_points_view`.`player_id` = `players_all_time`.`player_id`
GROUP BY `baseball`.`players_all_time`.`player_id`

########################################################
# players_least_points_view

SELECT
    `players_all_time`.`player_id`,
    MIN(`players_all_time`.`points`) AS least_points
FROM `baseball`.`players_all_time`
GROUP BY `baseball`.`players_all_time`.`player_id`

########################################################
# players_worst_year

SELECT 
    `players_least_points_view`.`player_id`,
    `players_least_points_view`.`least_points`,
    MAX(`players_all_time`.`season`) AS season
FROM
    `players_least_points_view`, `players_all_time`
WHERE
    `players_least_points_view`.`least_points` = `players_all_time`.`points`
    AND
    `players_least_points_view`.`player_id` = `players_all_time`.`player_id`
GROUP BY `baseball`.`players_all_time`.`player_id`



########################################################

SELECT 
    `players`.`player_id` AS `player_id`,
    `players`.`first_name` AS `first_name`,
    `players`.`first_name_plain` AS `first_name_plain`,
    `players`.`last_name` AS `last_name`,
    `players`.`last_name_plain` AS `last_name_plain`,
    `players`.`middle_initial` AS `middle_initial`,
    `players`.`suffix` AS `suffix`,
    `players`.`fnf` AS `fnf`,
    `players`.`lnf` AS `lnf`,
    `players`.`espn_stats_id` AS `espn_stats_id`,
    `players`.`year_added` AS `year_added`,
    `players`.`active` AS `active`,
    MIN(`players_all_time`.`season`) AS `rookie_year`,
    MAX(`players_all_time`.`points`) AS `most_points`,
    MIN(`players_all_time`.`points`) AS `least_points`
FROM
    (`players`
    JOIN `players_all_time`)
WHERE
    (`players`.`player_id` = `players_all_time`.`player_id`)
GROUP BY `players_all_time`.`player_id`