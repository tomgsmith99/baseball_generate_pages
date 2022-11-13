
SELECT 
    `baseball`.`o`.`owner_id` AS `owner_id`,
    `baseball`.`o`.`nickname` AS `nickname`,
    `baseball`.`o`.`head_shot` AS `owner_img`,
    `baseball`.`oxry`.`rookie_year` AS `rookie_year`,
    `baseball`.`oxmra`.`most_recent_appearance` AS `most_recent_appearance`,
    `baseball`.`oxbf`.`best_finish` AS `best_finish`,
    `baseball`.`oxac`.`appearances_count` AS `appearances_count`,
    `baseball`.`oxar`.`appearances_rank` AS `appearances_rank`,
    `baseball`.`oxcc`.`championships_count` AS `championships_count`,
    `baseball`.`oxcr`.`championships_rank` AS `championships_rank`,
    `baseball`.`oxr`.`rating` AS `rating`,
    `baseball`.`oxrr`.`rating_rank` AS `rating_rank`,
    `baseball`.`oxtsfc`.`top_six_finishes_count` AS `top_six_finishes_count`,
    `baseball`.`oxtsfr`.`top_six_finishes_rank` AS `top_six_finishes_rank`

FROM `baseball`.`owner_valid` `o`
    LEFT JOIN `baseball`.`owner_x_rookie_year` `oxry` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxry`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_most_recent_appearance` `oxmra`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxmra`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_best_finish` `oxbf`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxbf`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_appearances_count` `oxac`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxac`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_appearances_rank` `oxar`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxar`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_championships_count` `oxcc`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxcc`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_championships_rank` `oxcr`
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxcr`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_rating` `oxr` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxr`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_rating_rank` `oxrr` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxrr`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_top_six_finishes_count` `oxtsfc` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxtsfc`.`owner_id`

    LEFT JOIN `baseball`.`owner_x_top_six_finishes_rank` `oxtsfr` 
    ON `baseball`.`o`.`owner_id` = `baseball`.`oxtsfr`.`owner_id`
