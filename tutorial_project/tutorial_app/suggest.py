from models import Category

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    if cat_list and max_results > 0:
        if cat_list.count() > max_results:
            cat_list = cat_list[:max_results]
    return cat_list