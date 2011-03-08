from django.db import connection

qn = connection.ops.quote_name

COUNT_SUBQUERY = """(
    %(mptt_fk)s = %(mptt_table)s.%(mptt_pk)s
)"""

CUMULATIVE_COUNT_SUBQUERY = """(
    %(mptt_fk)s IN
    (
        SELECT m2.%(mptt_pk)s
        FROM %(mptt_table)s m2
        WHERE m2.%(tree_id)s = %(mptt_table)s.%(tree_id)s
          AND m2.%(left)s BETWEEN %(mptt_table)s.%(left)s
                              AND %(mptt_table)s.%(right)s
    )
)"""

def add_filtered_related_count(manager, queryset, rel_queryset, rel_field, count_attr,
                       cumulative=False):
    opts = manager.model._meta
    rel_model = rel_queryset.model
    if cumulative:
        rel_queryset = rel_queryset.extra(where=[CUMULATIVE_COUNT_SUBQUERY % {
             'mptt_fk': qn(rel_model._meta.get_field(rel_field).column),
             'mptt_table': qn(opts.db_table),
             'mptt_pk': qn(opts.pk.column),
             'tree_id': qn(opts.get_field(manager.tree_id_attr).column),
             'left': qn(opts.get_field(manager.left_attr).column),
             'right': qn(opts.get_field(manager.right_attr).column),
        }])
    else:
        rel_queryset = rel_queryset.extra(where=[COUNT_SUBQUERY % {
            'mptt_fk': qn(rel_model._meta.get_field(rel_field).column),
            'mptt_table': qn(opts.db_table),
            'mptt_pk': qn(opts.pk.column),
        }])
    #rel_queryset.query.add_count_column()
    return queryset.extra(select={count_attr: rel_queryset.query})

