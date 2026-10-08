select md5(assignment_group) as group_key, assignment_group from {{ ref('stg_tickets') }} group by assignment_group
