
SELECT 
    `baseball`.`o`.`owner_id` AS `owner_id`,
    `baseball`.`o`.`nickname` AS `nickname`,
    `baseball`.`o`.`head_shot` AS `owner_img`,
    `baseball`.`oxry`.`rookie_year` AS `rookie_year`,
    `baseball`.`oxmra`.`most_recent_appearance` AS `most_recent_appearance`,
    `baseball`.`oxbf`.`best_finish` AS `best_finish`,
    `baseball`.`oxrd`.`rating` AS `rating`,
    `baseball`.`oxrd`.`rating_rank` AS `rating_rank`,
    `baseball`.`oxtsd`.`top_six_finishes_count` AS `top_six_finishes_count`,
    `baseball`.`oxtsd`.`top_six_finishes_rank` AS `top_six_finishes_rank`,
    `baseball`.`oxad`.`appearances_count` AS `appearances_count`,
    `baseball`.`oxad`.`appearances_rank` AS `appearances_rank`,
    `baseball`.`oxcd`.`championships_count` AS `championships_count`,
    `baseball`.`oxcd`.`championships_rank` AS `championships_rank`

FROM `baseball`.`owner_valid` `o`
    LEFT JOIN `baseball`.`owner_x_rookie_year` `oxry` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxry`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_most_recent_appearance` `oxmra` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxmra`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_best_finish` `oxbf`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxbf`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_rating_detail` `oxrd` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxrd`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_top_six_detail` `oxtsd` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxtsd`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_appearances_detail` `oxad`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxad`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_championships_detail` `oxcd`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxcd`.`owner_id`
