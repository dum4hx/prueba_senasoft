from django.contrib import admin
from .models import TipoIdentificacion, Usuarios, Aviones, Ciudades, Aeropuertos, Vuelos, Reservas, MetodosPago, Pagos, Tiquetes

class AdminTipoIdentificacion(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    
admin.site.register(TipoIdentificacion, AdminTipoIdentificacion)

class AdminUsuarios(admin.ModelAdmin):
    list_display = ('nombre', 'numero_identificacion','fk_tipo_identificacion', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'numero_identificacion')
    
admin.site.register(Usuarios, AdminUsuarios)

class AdminAviones(admin.ModelAdmin):
    list_display = ('fk_modelo_avion', 'matricula', 'activo')
    list_filter = ('fk_modelo_avion', 'activo')
    search_fields = ('matricula', 'fk_modelo_avion')

admin.site.register(Aviones, AdminAviones)

class AdminCiudades(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    
admin.site.register(Ciudades, AdminCiudades)

class AdminAeropuertos(admin.ModelAdmin):
    list_display = ('nombre', 'fk_ciudad', 'codigo_iata')
    list_filter = ('fk_ciudad',)
    search_fields = ('nombre', 'codigo_iata')
    
admin.site.register(Aeropuertos, AdminAeropuertos)

class AdminVuelos(admin.ModelAdmin):
    list_display = ('fk_avion', 'fk_aeropuerto_llegada', 'fk_aeropuerto_salida', 'fecha_hora_salida', 'fecha_hora_llegada')
    list_filter = ('fk_aeropuerto_salida', 'fk_aeropuerto_llegada')
    search_fields = ('fk_avion',)

admin.site.register(Vuelos, AdminVuelos)

class AdminReservas(admin.ModelAdmin):
    list_display = ('fk_vuelo', 'fk_usuario')
    list_filter = ('fk_vuelo', 'fk_usuario')
    search_fields = ('fk_vuelo',)
    
admin.site.register(Reservas, AdminReservas)

class AdminMetodosPago(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    
admin.site.register(MetodosPago, AdminMetodosPago)

class AdminPagos(admin.ModelAdmin):
    list_display = ('fk_metodo_pago', 'fk_reserva', 'monto', 'pagado')
    list_filter = ('fk_metodo_pago',)
    search_fields = ('monto', 'fk_metodo_pago')
    
admin.site.register(Pagos, AdminPagos)

class AdminTiquetes(admin.ModelAdmin):
    list_display = ('fk_pago', 'activo')
    list_filter = ('fk_pago',)

admin.site.register(Tiquetes, AdminTiquetes)

