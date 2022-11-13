    SELECT 
        `baseball`.`finishes`.`owner_id` AS `owner_id`,
        COUNT(`baseball`.`finishes`.`season`) AS `top_six_finishes_count`
    FROM
        `baseball`.`finishes`
    GROUP BY `baseball`.`finishes`.`owner_id` 
    UNION ALL SELECT 
        `o`.`owner_id` AS `owner_id`, 0 AS `top_six_finishes`
    FROM
        `baseball`.`owners` `o`
    WHERE
        `o`.`owner_id` IN (SELECT DISTINCT
                `baseball`.`finishes`.`owner_id`
            FROM
                `baseball`.`finishes`)
            IS FALSE

    SELECT 
        `baseball`.`o`.`owner_id` AS `owner_id`,
        COUNT(`baseball`.`oxc`.`season`) AS `championships_count`
    FROM
        (`baseball`.`owner_valid` `o`
        LEFT JOIN `baseball`.`owner_x_championships` `oxc` ON ((`baseball`.`o`.`owner_id` = `baseball`.`oxc`.`owner_id`)))
    GROUP BY `baseball`.`o`.`owner_id`

    SELECT 
        `baseball`.`o`.`owner_id` AS `owner_id`,
        COUNT(`baseball`.`oxtsf`.`season`) AS `top_six_finishes_count`
    FROM `baseball`.`owner_valid` `o`
        LEFT JOIN `baseball`.`owner_x_top_six_finishes` `oxtsf` ON 
        ((`baseball`.`o`.`owner_id` = `baseball`.`oxc`.`owner_id`)))
    GROUP BY `baseball`.`o`.`owner_id`

