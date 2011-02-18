'''
Simple order partitioner

Gets whatever products are left in the cart and puts them all in a single
delivery group.
'''

def partition(cart, items):
    handled_groups = [list(items)]
    remaining_items = ()
    return handled_groups, remaining_items
