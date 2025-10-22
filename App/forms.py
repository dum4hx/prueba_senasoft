from django import forms
from .models import TipoIdentificacion, Usuarios

class FormUsuarios(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ['nombre', 'numero_identificacion', 'celular', 'email', 'fk_tipo_identificacion']
        exclude = ['user', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        
        