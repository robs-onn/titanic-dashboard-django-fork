from django.shortcuts import render
import pandas as pd
from dashboard.models import TitanicPassenger
from django.db.models import Count, Sum, F

# Create your views here.
def index(request):
    context = {}

    total_passenger = TitanicPassenger.objects.count()
    context["total_passenger"] = total_passenger

    total_male = TitanicPassenger.objects.filter(sex="male").count()
    context["total_male"] = total_male
    
    context["total_female"] = total_passenger - total_male
    
    total_fare = sum(TitanicPassenger.objects.values_list("fare", flat=True))
    context["total_fare"] = "$ " + str(int(total_fare // 1000)) + "K"

    total_survived = TitanicPassenger.objects.filter(survived=1).count()
    context["total_survived"] = total_survived
    context["survived_rate"] = round(total_survived / total_passenger * 100, 2)

    classes_lista = TitanicPassenger.objects.values_list('pclass', flat=True).distinct().order_by('pclass')
    classes = list(classes_lista)
    context["classes"] = classes

    counts_q = TitanicPassenger.objects.values('pclass').annotate(count=Count('id')).order_by('pclass')
    count_by_class = [item['count'] for item in counts_q]
    context["count_by_class"] = count_by_class

    survived_q = TitanicPassenger.objects.values('pclass').annotate(total_survived=Sum('survived')).order_by('pclass')
    survived_by_class = [item['total_survived'] for item in survived_q]
    context["survived_by_class"] = survived_by_class

    died_by_class = [total - survived for total, survived in zip(count_by_class, survived_by_class)]
    context["died_by_class"] = died_by_class

    top_10_fares = TitanicPassenger.objects.order_by('-fare').values(Name=F('name'), Fare=F('fare'))[:10]
    context["top_10_fares"] = list(top_10_fares)

    ports_q = TitanicPassenger.objects.exclude(embarked=None).values_list('embarked', flat=True).distinct().order_by('embarked')
    ports = list(ports_q)
    context["ports"] = ports
    
    embarked_q = TitanicPassenger.objects.exclude(embarked=None).filter(survived=1).values('embarked', 'pclass').annotate(count=Count('id')).order_by('embarked', 'pclass')

    pivot_data = {port: {p_class: 0 for p_class in classes} for port in ports}
    
    for item in embarked_q : pivot_data[item['embarked']][item['pclass']] = item['count']
    
    embarked_by_class_list = []
    for port in ports:
        row = [pivot_data[port][p_class] for p_class in classes]
        embarked_by_class_list.append(row)
        
    embarked_by_class = embarked_by_class_list[::-1]
    context["embarked_by_class"] = embarked_by_class

    return render(request, "dashboard/index.html", context=context)
