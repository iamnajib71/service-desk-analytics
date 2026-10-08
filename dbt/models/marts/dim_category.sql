select md5(category) as category_key, category from {{ ref('stg_tickets') }} group by category
