from django.db import models

class House(models.Model):
    street_name = models.CharField('Название улицы', max_length=255)
    house_number = models.CharField('Номер дома', max_length=50)
    def __str__(self):
        return f"{self.street_name}, дом {self.house_number}"

    def get_absolute_url(self):
        return f'/houses/{self.id}'

    class Meta:
        verbose_name = "Дом"
        verbose_name_plural = "Дома"

class Apartment(models.Model):
    house = models.ForeignKey(House, related_name='apartments', on_delete=models.CASCADE)
    number = models.CharField('Номер квартиры', max_length=255)
    area = models.IntegerField('Площадь квартиры')

    def __str__(self):
        return f"Квартира №{self.number} на улице {self.house.street_name} {self.house.house_number}"

    class Meta:
        verbose_name = "Квартира"
        verbose_name_plural = "Квартиры"

class WaterMeter(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='water_meters', on_delete=models.CASCADE)

    def __str__(self):
        return f"Счетчик воды {self.id} в {self.apartment}"

    class Meta:
        verbose_name = "Счетчик"
        verbose_name_plural = "Счетчики"

class WaterMeterReading(models.Model):
    water_meter = models.ForeignKey(WaterMeter, related_name='readings', on_delete=models.CASCADE)
    reading = models.IntegerField('Показание')
    date = models.DateField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = "Показание счетчика"
        verbose_name_plural = "Показания счетчиков"

class Tariff(models.Model):
    service = models.CharField(max_length=255)
    price_per_unit = models.FloatField(f"Цена за услугу")

    def __str__(self):
        return f"Тариф на {self.service} по {self.price_per_unit}/р."

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

class Payment(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    payment_number = models.IntegerField('Номер платежа', default=1)
    water_supply_charge = models.FloatField('Плата за водоснабжение')
    common_property_charge = models.FloatField('Плата за содержание общего имущества')
    total_charge = models.FloatField('Общая квартплата')

    def __str__(self):
        return f"Платеж #{self.payment_number} для {self.apartment}"

    class Meta:
        unique_together = ('apartment', 'payment_number')
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"




class CalculationProgress(models.Model):
    house_id = models.IntegerField()
    payment_number = models.IntegerField()
    completed_apartments = models.IntegerField(default=0)
    total_apartments = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('house_id', 'payment_number')