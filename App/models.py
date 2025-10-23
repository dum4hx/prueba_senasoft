from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

class TipoIdentificacion(models.Model):
    
    idTipoIdentificacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tipo_Identificacion'
        verbose_name_plural = 'Tipos_Identificacion'
        db_table = 'Tipos_Identificacion'
        
    def __str__(self):
        return self.nombre

class Usuarios(models.Model):
    
    idUsuario = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    nombre = models.CharField(max_length=50)
    primer_apellido = models.CharField(max_length=50,default=None, null=True)
    segundo_apellido = models.CharField(max_length=50, default=None, null=True)
    fecha_nacimiento = models.DateField(default=None, null=True)
    generos = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    ]
    genero = models.CharField(max_length=10, choices=generos, default=None, null=True)
    contraseña = models.CharField(max_length=128)
    numero_identificacion = models.CharField(max_length=50)
    fk_tipo_identificacion = models.ForeignKey(TipoIdentificacion, on_delete=models.CASCADE)
    celular = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    es_infante = models.BooleanField(default=False, null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'Usuarios'
        
    def __str__(self):
        return f"Usuario: {self.nombre} - Numero: {self.numero_identificacion}"
    
@receiver(post_save, sender=Usuarios)
def calcular_es_infante(sender, instance, **kwargs):
    if instance.fecha_nacimiento:
        hoy = date.today()
        edad = hoy.year - instance.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (instance.fecha_nacimiento.month, instance.fecha_nacimiento.day)
        )

        es_infante = edad < 3

        if instance.es_infante != es_infante:
            instance.es_infante = es_infante
            instance.save(update_fields=['es_infante'])
    
@receiver(post_save, sender=Usuarios)
def crear_usuario_user(sender, instance, created, **kwargs):
    """
    Cada vez que se cree un Usuario, se genera un User asociado automáticamente.
    """
    if created and not instance.user:
        
        username = instance.numero_identificacion
       
        password = instance.contraseña

        first_name = instance.nombre

        email = instance.email

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            email=email
        )

        instance.user = user
        instance.save()

class ModelosAviones(models.Model):
    
    idModeloAvion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    capacidad_pasajeros = models.IntegerField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Modelo_Avion'
        verbose_name_plural = 'Modelos_Aviones'
        db_table = 'Modelos_Aviones'

    def __str__(self):
        return f"Nombre: {self.nombre} - Capacidad: {self.capacidad_pasajeros} pasajeros" 
    
class Aviones(models.Model):
    
    idAvion = models.AutoField(primary_key=True)
    fk_modelo_avion = models.ForeignKey(ModelosAviones, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Avion'
        verbose_name_plural = 'Aviones'
        db_table = 'Aviones'

    def __str__(self):
        return f"Avion Serie: {self.matricula} - Modelo: {self.fk_modelo_avion.nombre}"
    
class Ciudades(models.Model):
    
    idCiudad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        db_table = 'Ciudades'

    def __str__(self):
        return f"{self.nombre}"
    
class Aeropuertos(models.Model):
    
    idAeropuerto = models.AutoField(primary_key=True)
    fk_ciudad = models.ForeignKey(Ciudades, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    codigo_iata = models.CharField(max_length=10, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Aeropuerto'
        verbose_name_plural = 'Aeropuertos'
        db_table = 'Aeropuertos'

    def __str__(self):
        return f"{self.nombre} ({self.codigo_iata})"
    
class Vuelos(models.Model):
    
    idVuelo = models.AutoField(primary_key=True)
    fk_avion = models.ForeignKey(Aviones, on_delete=models.CASCADE)
    fk_aeropuerto_salida = models.ForeignKey(Aeropuertos, on_delete=models.CASCADE, related_name='aeropuerto_salida')
    fk_aeropuerto_llegada = models.ForeignKey(Aeropuertos, on_delete=models.CASCADE, related_name='aeropuerto_llegada')
    fecha_hora_salida = models.DateTimeField()
    fecha_hora_llegada = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Vuelo'
        verbose_name_plural = 'Vuelos'
        db_table = 'Vuelos'

    def __str__(self):
        return f"Avion: {self.fk_avion.matricula} - Salida: {self.fk_aeropuerto_salida.nombre} - Llegada: {self.fk_aeropuerto_llegada.nombre}"
    
class Reservas(models.Model):
    
    idReserva = models.AutoField(primary_key=True)
    fk_vuelo = models.ForeignKey(Vuelos, on_delete=models.CASCADE)
    fk_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fk_pasajero = models.ForeignKey(Usuarios, on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='pasajero_reserva')
    asiento = models.CharField(max_length=3, default=None)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        db_table = 'Reservas'

    def __str__(self):
        return f"Vuelo: {self.fk_vuelo.idVuelo} - Usuario: {self.fk_usuario.nombre}"
    
class MetodosPago(models.Model):
    
    idMetodoPago = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Metodo_Pago'
        verbose_name_plural = 'Metodos_Pago'
        db_table = 'Metodos_Pago'

    def __str__(self):
        return self.nombre
    
class Pagos(models.Model):
    
    idPago = models.AutoField(primary_key=True)
    fk_metodo_pago = models.ForeignKey(MetodosPago, on_delete=models.CASCADE)
    fk_reserva = models.ForeignKey(Reservas, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        db_table = 'Pagos'

    def __str__(self):
        return f"Reserva: {self.fk_reserva.idReserva} - Monto: {self.monto}"
    
class Tiquetes(models.Model):
    
    idTiquete = models.AutoField(primary_key=True)
    fk_pago = models.ForeignKey(Pagos, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_actualizacion = models.DateField(auto_now=True)
    

    class Meta:
        verbose_name = 'Tiquete'
        verbose_name_plural = 'Tiquetes'
        db_table = 'Tiquetes'

    def __str__(self):
        return f"Tiquete Codigo: {self.codigo} - Pago: {self.fk_pago.idPago}"
    

    
