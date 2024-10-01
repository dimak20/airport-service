from django.contrib import admin

from air_service.models import (
    Country,
    City,
    Crew,
    AirplaneType,
    Airport,
    Airplane,
    Route,
    Flight,
    Ticket,
    Order
)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInLine, )


admin.site.register(Country)
admin.site.register(Ticket)
admin.site.register(City)
admin.site.register(Crew)
admin.site.register(AirplaneType)
admin.site.register(Airport)
admin.site.register(Airplane)
admin.site.register(Route)
admin.site.register(Flight)
