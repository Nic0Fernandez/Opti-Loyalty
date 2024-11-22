from django.shortcuts import render
from django.conf import settings
from menu.get_menu import get_menu
from collections import defaultdict

# Create your views here.

def menu(request):
    db_path = settings.DATABASES['default']['NAME']
    pizzas = get_menu(db_path)

    # Grouper les pizzas par catégorie
    categories = defaultdict(list)
    for pizza in pizzas:
        categories[pizza['category']].append(pizza)

    # Pour chaque catégorie, grouper les pizzas par nom et agréger les tailles et prix
    grouped_categories = {}
    for category, pizzas_in_category in categories.items():
        grouped_pizzas = defaultdict(list)
        for pizza in pizzas_in_category:
            key = (pizza['name'], pizza['ingredients'], pizza['image']) 
            grouped_pizzas[key].append({'size': pizza['size'], 'unit_price': pizza['unit_price']})

        unique_pizzas = []
        for (name, ingredients, image), sizes in grouped_pizzas.items():
            sorted_sizes = sorted(sizes, key=lambda x: x['unit_price'])
            unique_pizzas.append({
                'name': name,
                'ingredients': ingredients,
                'image': image,
                'sizes': sorted_sizes
            })

        grouped_categories[category] = unique_pizzas

    context = {
        'grouped_categories': grouped_categories,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'menu/menu.html', context)


from django.shortcuts import render

def test_turn(request):
    return render(request, 'menu/test_turn.html')
