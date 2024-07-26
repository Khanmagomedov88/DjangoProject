from django.shortcuts import render, redirect, get_object_or_404
from .models import House, Apartment, Tariff, WaterMeter, WaterMeterReading, Payment
from django.db import transaction
from .forms import HouseForm, ApartmentForm, TariffForm, WaterMeterForm
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse
from django.http import JsonResponse
from .tasks import calculate_monthly_charges

def index(request):
    data = {
        'title': 'Главная страница',
        }
    return render(request, 'main/index.html', data)

def houses(request):
    houses = House.objects.all
    data = {
        'title': 'Список домов',
        'houses': houses,
        }
    return render(request, 'main/houses.html', data)

class HouseDetailView(DetailView):
    model = House
    template_name = 'main/details_view.html'
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartments'] = self.object.apartments.all()
        return context

def edit_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    house_id = apartment.house.id

    if request.method == 'POST':
        form = ApartmentForm(request.POST, instance=apartment)
        if form.is_valid():
            form.save()
            return redirect('house-detail', pk=house_id)
    else:
        form = ApartmentForm(instance=apartment)

    return render(request, 'main/createApartment.html', {'form': form})

def delete_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    if request.method == 'POST':
        apartment.delete()
        return redirect('houses')
    return render(request, 'main/deleteApartment.html', {'apartment': apartment})

class HouseUpdateView(UpdateView):
    model = House
    template_name = 'main/createHouse.html'

    form_class = HouseForm

class ApartmentUpdateView(UpdateView):
    model = Apartment
    template_name = 'main/createApartment.html'

    form_class = ApartmentForm

class HouseDeleteView(DeleteView):
    model = House
    success_url = f'/houses'
    template_name = 'main/deleteHouse.html'


def addApartment(request, pk):
    house = get_object_or_404(House, pk=pk)
    error = ''

    if request.method == 'POST':
        formApartment = ApartmentForm(request.POST, house=house)
        if formApartment.is_valid():
            apartment = formApartment.save(commit=False)
            apartment.house = house
            apartment.save()

            return redirect(reverse('house-detail', args=[house.id]))
        else:
            if 'number' in formApartment.errors:
                error = formApartment.errors['number'][0]
            else:
                error = "Форма заполнена некорректно!"
    else:
        formApartment = ApartmentForm(house=house)

    data = {
        'formApartment': formApartment,
        'error': error,
        'house': house
    }
    return render(request, 'main/addApartment.html', data)

def addHouse(request):
    error = ''
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            street_name = form.cleaned_data.get('street_name')
            house_number = form.cleaned_data.get('house_number')
            if House.objects.filter(street_name=street_name, house_number=house_number).exists():
                error = "Дом с таким адресом уже существует!"
            else:
                form.save()
                return redirect('houses')
        else:
            error = "Форма заполнена некорректно!"

    form = HouseForm()
    data = {
        'form': form,
        'error': error,
    }
    return render(request, 'main/addHous.html', data)

def apartment_detail(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    water_meters = apartment.water_meters.all()

    try:
        water_tariff = Tariff.objects.get(service='Водоснабжение')
    except Tariff.DoesNotExist:
        water_tariff = None
        water_charge = 0
    else:
        water_charge = 0

    try:
        common_property_tariff = Tariff.objects.get(service='Содержание общего имущества')
    except Tariff.DoesNotExist:
        common_property_tariff = None
        common_property_charge = 0
    else:
        common_property_charge = apartment.area * common_property_tariff.price_per_unit

    if request.method == 'POST':
        if 'update_meter' in request.POST:
            meter_id = request.POST.get('meter_id')
            meter = get_object_or_404(WaterMeter, id=meter_id)
            form = WaterMeterForm(request.POST)
            if form.is_valid():
                new_reading = form.cleaned_data['reading']
                WaterMeterReading.objects.create(water_meter=meter, reading=new_reading)
                return redirect('apartment_detail', apartment_id=apartment_id)

        elif 'delete_meter' in request.POST:
            meter_id = request.POST.get('meter_id')
            meter = get_object_or_404(WaterMeter, id=meter_id)
            meter.delete()
            return redirect('apartment_detail', apartment_id=apartment_id)

    forms = {meter.id: WaterMeterForm() for meter in water_meters}
    if water_meters.exists() and water_tariff:
        total_water_charge = 0

        for meter in water_meters:
            readings = meter.readings.all().order_by('date')
            if readings.exists():
                if readings.count() >= 2:
                    last_reading = readings[readings.count() - 1].reading
                    second_last_reading = readings[readings.count() - 2].reading
                    usage = last_reading - second_last_reading
                else:
                    usage = readings.last().reading
                total_water_charge += usage * water_tariff.price_per_unit

        water_charge = total_water_charge

    total_charge = water_charge + common_property_charge

    return render(request, 'main/apartment_detail.html', {
        'apartment': apartment,
        'water_meters': water_meters,
        'forms': forms,
        'water_charge': water_charge,
        'common_property_charge': common_property_charge,
        'total_charge': total_charge,
    })


def add_water_meter(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    house = apartment.house
    existing_meters = apartment.water_meters.all()

    if request.method == 'POST':
        form = WaterMeterForm(request.POST)
        if form.is_valid():
            new_reading = form.cleaned_data['new_reading']
            water_meter = WaterMeter(apartment=apartment)
            water_meter.save()
            WaterMeterReading.objects.create(water_meter=water_meter, reading=new_reading)
            return redirect(reverse('apartment_detail', args=[apartment_id]))
        else:
            print(form.errors)  # Debug: вывод ошибок формы
    else:
        form = WaterMeterForm()

    return render(request, 'main/add_water_meter.html', {
        'form': form,
        'apartment': apartment,
        'house': house,
        'existing_meters': existing_meters,

    })

def add_tariff(request):
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tariffs')
    else:
        form = TariffForm()

    return render(request, 'main/add_tariff.html', {'form': form})

def edit_tariff(request, tariff_id):
    tariff = get_object_or_404(Tariff, id=tariff_id)
    if request.method == 'POST':
        form = TariffForm(request.POST, instance=tariff)
        if form.is_valid():
            form.save()
            return redirect('tariffs')
    else:
        form = TariffForm(instance=tariff)
    return render(request, 'main/edit_tariff.html', {'form': form})

def delete_tariff(request, tariff_id):
    tariff = get_object_or_404(Tariff, id=tariff_id)
    if request.method == 'POST':
        tariff.delete()
        return redirect('tariffs')
    return render(request, 'main/delete_tariff.html', {'tariff': tariff})

def tariff_list(request):
    tariffs = Tariff.objects.all()
    return render(request, 'main/tariff_list.html', {'tariffs': tariffs})

def calculate_charges_view(request, house_id, payment_number):
    result = calculate_monthly_charges.delay(house_id, payment_number)
    return JsonResponse({'task_id': result.id, 'status': 'Calculation started'})


def calculate_rent_for_all_apartments(house_id):
    house = House.objects.get(id=house_id)
    apartments = house.apartments.all()

    try:
        water_tariff = Tariff.objects.get(service='Водоснабжение')
    except Tariff.DoesNotExist:
        water_tariff = None

    try:
        common_property_tariff = Tariff.objects.get(service='Содержание общего имущества')
    except Tariff.DoesNotExist:
        common_property_tariff = None

    results = []

    for apartment in apartments:
        water_charge = 0
        common_property_charge = 0

        if water_tariff:
            for meter in apartment.water_meters.all():
                readings = meter.readings.all().order_by('date')
                if readings.count() >= 2:
                    last_reading = readings[readings.count() - 1].reading
                    second_last_reading = readings[readings.count() - 2].reading
                    usage = last_reading - second_last_reading
                else:
                    usage = readings.last().reading if readings.exists() else 0

                water_charge += usage * water_tariff.price_per_unit

        if common_property_tariff:
            common_property_charge = apartment.area * common_property_tariff.price_per_unit

        total_charge = water_charge + common_property_charge

        with transaction.atomic():
            payment = Payment.objects.create(
                apartment=apartment,
                water_supply_charge=water_charge,
                common_property_charge=common_property_charge,
                total_charge=total_charge
            )

        results.append({
            'apartment_number': apartment.number,
            'water_charge': water_charge,
            'common_property_charge': common_property_charge,
            'total_charge': total_charge
        })

    return results

def calculate_rent_view(request, house_id):
    house = get_object_or_404(House, id=house_id)
    result = calculate_rent_for_all_apartments(house_id)
    return render(request, 'main/calculate_rent_result.html', {'result': result, 'house': house})