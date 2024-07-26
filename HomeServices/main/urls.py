from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('houses/', views.houses, name='houses'),
    path('houses/addhouse/', views.addHouse, name='addHouse'),
    path('houses/<int:pk>', views.HouseDetailView.as_view(), name='house-detail'),
    path('houses/<int:pk>/updatehouse', views.HouseUpdateView.as_view(), name='house-update'),
    path('houses/<int:pk>/deletehouse', views.HouseDeleteView.as_view(), name='house-delete'),
    path('houses/<int:pk>/addapartment/', views.addApartment, name='addApartment'),
    path('apartment/edit/<int:apartment_id>/', views.edit_apartment, name='edit_apartment'),
    path('apartment/delete/<int:apartment_id>/', views.delete_apartment, name='delete_apartment'),
    path('apartment/<int:apartment_id>/add_water_meter/', views.add_water_meter, name='add_water_meter'),
    path('apartment/<int:apartment_id>/', views.apartment_detail, name='apartment_detail'),
    path('add-tariff/', views.add_tariff, name='add_tariff'),
    path('tariffs/', views.tariff_list, name='tariffs'),
    path('edit/<int:tariff_id>/', views.edit_tariff, name='edit_tariff'),
    path('delete/<int:tariff_id>/', views.delete_tariff, name='delete_tariff'),
    path('calculate_rent/<int:house_id>/', views.calculate_rent_view, name='calculate_rent'),

]
