from django.shortcuts import render
from rest_framework import viewsets

from air_service.models import Country
from air_service.serializers import CountrySerializer


class CountryViewSet(viewsets.ModelViewSet):
    model = Country
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
