from django import forms
from .models import House, Apartment, WaterMeter, Tariff, WaterMeterReading
from django.forms import ModelForm, TextInput


class HouseForm(ModelForm):
    class Meta:
        model = House
        fields = ['street_name', 'house_number']

        widgets = {
            'street_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название улицы'
            }),
            'house_number': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер дома'
            })
        }

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['number', 'area']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер квартиры'
            }),
            'area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Площадь квартиры'
            })
        }

    def __init__(self, *args, **kwargs):
        self.house = kwargs.pop('house', None)
        super().__init__(*args, **kwargs)

    def clean_number(self):
        number = self.cleaned_data.get('number')
        if self.house:
            if Apartment.objects.filter(house=self.house, number=number).exists():
                raise forms.ValidationError('Квартира с таким номером уже существует в этом доме.')
        return number


class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['service', 'price_per_unit']


        widgets = {
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Стоимость тарифа',
                'min': '0',
                'step': '0.01',
            }),
            'service': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название тарифа'
            })
        }

class WaterMeterReadingForm(forms.ModelForm):
    class WaterMeterReadingForm(forms.ModelForm):
        class Meta:
            model = WaterMeterReading
            fields = ['reading']

class WaterMeterForm(forms.Form):
    new_reading = forms.IntegerField(
        label='Новое показание счетчика',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Новое показание'})
    )


class AddReadingForm(forms.Form):
    reading = forms.IntegerField(label='Новое показание')

    def clean_reading(self):
        reading = self.cleaned_data['reading']
        meter_id = self.initial['meter_id']
        meter = WaterMeter.objects.get(id=meter_id)
        if meter.readings and reading < meter.readings[0]:
            raise forms.ValidationError("Новое показание не может быть меньше предыдущего.")
        return reading


class PaymentNumberForm(forms.Form):
    payment_number = forms.IntegerField(
        label='Номер платежа',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Номер платежа'})
    )