from celery import shared_task
from django.db import transaction
from .models import Apartment, Tariff, Payment, CalculationProgress


@shared_task
def calculate_monthly_charges(house_id, payment_number):
    apartments = Apartment.objects.filter(house_id=house_id)

    progress, created = CalculationProgress.objects.get_or_create(
        house_id=house_id,
        payment_number=payment_number,
        defaults={'total_apartments': apartments.count()}
    )

    if progress.is_completed:
        return "Calculation already completed for this payment number."

    try:
        with transaction.atomic():
            for apartment in apartments[progress.completed_apartments:]:
                water_meters = apartment.water_meters.all()
                total_water_charge = 0

                for meter in water_meters:
                    readings = meter.readings.all().order_by('date')
                    if readings.exists():
                        if readings.count() >= 2:
                            last_reading = readings.last().reading
                            second_last_reading = readings[readings.count() - 2].reading
                            usage = last_reading - second_last_reading
                        else:
                            usage = readings.last().reading

                        water_tariff = Tariff.objects.get(service='Водоснабжение')
                        total_water_charge += usage * water_tariff.price_per_unit

                try:
                    common_property_tariff = Tariff.objects.get(service='Содержание общего имущества')
                    common_property_charge = apartment.area * common_property_tariff.price_per_unit
                except Tariff.DoesNotExist:
                    common_property_charge = 0

                total_charge = total_water_charge + common_property_charge

                Payment.objects.create(
                    apartment=apartment,
                    payment_number=payment_number,
                    water_supply_charge=total_water_charge,
                    common_property_charge=common_property_charge,
                    total_charge=total_charge
                )

                progress.completed_apartments += 1
                progress.save()

            progress.is_completed = True
            progress.save()

            return "Calculation completed successfully."

    except Exception as e:
        return f"An error occurred: {e}"
