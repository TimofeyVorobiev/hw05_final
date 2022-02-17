from datetime import date


def year(request):
    current_date = date.today().year
    context = {
        'year': current_date
    }
    return context
