from django import forms
from .models import JugadoraPorAno,  Categoria, Division, Jugadora, EstadoJugadora


class JugadoraForm(forms.Form):
    class Meta:
        model = Jugadora
        fields = ['nombre', 'apellido', 'dni', 'fecha_nacimiento', 'categoria', 'division']  

    nombre = forms.CharField(
        max_length=100,
        required=True,
        label='Nombre'
    )
    apellido = forms.CharField(
        max_length=100, 
        required=True,
        label='Apellido'
    )
    fecha_nacimiento = forms.DateField(
        required=True,
        label='Fecha de Nacimiento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    dni = forms.CharField(
        max_length=20,
        required=True, 
        label='DNI'
    )
    num_socia = forms.CharField(
        max_length=20,
        required=False,
        label='Número de socia'
    )
    ano = forms.IntegerField(
        required=True,
        label='Año',
        min_value=1945,
        max_value=2100
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=True,
        label='Categoría',
        to_field_name='nombre'
    )
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(), 
        required=True,
        label='División',
        to_field_name='nombre'
    )

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números")
        return dni

    def clean(self):
        cleaned_data = super().clean()
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        ano = cleaned_data.get('ano')
        
        if fecha_nacimiento and ano:
            if fecha_nacimiento.year > ano:
                raise forms.ValidationError(
                    "La fecha de nacimiento no puede ser posterior al año seleccionado"
                )
        return cleaned_data

class FiltroJugadorasForm(forms.Form):
    ano = forms.IntegerField(label='Año')
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        label='Categoría',
        to_field_name='nombre'  # Usar el campo nombre en lugar del id
    )
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        label='División',
        to_field_name='nombre'  # Usar el campo nombre en lugar del id
    )

#-------------------------------------------------------------------------------------------
#----Seleccionar Jugadoras-----------------------------------------------------------------


class SeleccionForm(forms.Form):
    ano_seleccion = forms.IntegerField(
        label='Año de destino',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    jugadoras = forms.ModelMultipleChoiceField(
        queryset=JugadoraPorAno.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    def clean(self):
        cleaned_data = super().clean()
        jugadoras = cleaned_data.get('jugadoras')
        if jugadoras and not jugadoras.exists():
            self.add_error('jugadoras', "Debe seleccionar al menos una jugadora.")
        return cleaned_data

class SeleccionJugadoraForm(forms.Form):
    ano = forms.IntegerField(label="Año", required=True)
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), label="Categoría")
    division = forms.ModelChoiceField(queryset=Division.objects.all(), label="División")
    jugadoras = forms.ModelMultipleChoiceField(
        queryset=Jugadora.objects.filter(activa=True),
        widget=forms.CheckboxSelectMultiple,
        label="Jugadoras"
    )
    
#-------------------------------------------------------------------------------------------
#----Gestionar Jugadoras por Año-----------------------------------------------------------
    
class FiltroJugadorasForm1(forms.Form):
    
    ano = forms.ModelChoiceField(
        queryset=JugadoraPorAno.objects.values_list('ano', flat=True).distinct().order_by('ano'),
        label='Año',
        to_field_name='ano'
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        label='Categoría', 
        to_field_name='nombre'  # Usar el campo nombre en lugar del id
    )

#-------------------------------------------------------------------------------------------
#----Detalle de Jugadora---------------------------------------------------------------
class BuscarJugadoraForm(forms.Form):
    apellido = forms.CharField(
        label='Apellido',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese apellido'})
    )
    nombre = forms.CharField(
        label='Nombre',
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombre'})
    )

class JugadoraDetalleForm(forms.Form):
    # Información básica de la jugadora
    nombre = forms.CharField(
        label='Nombre',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True})
    )
    apellido = forms.CharField(
        label='Apellido', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True})
    )
    dni = forms.IntegerField(
        label='DNI',
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True})
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'readonly': True})
    )
    num_socia = forms.IntegerField(
        label='Número de Socia',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True})
    )
    activa = forms.BooleanField(
        label='Activa',
        required=False,
        widget=forms.CheckboxInput(attrs={'disabled': True})
    )

    # Historial por año
    historial = forms.ModelChoiceField(
        queryset=JugadoraPorAno.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        empty_label="Seleccione un año"
    )
    

    def __init__(self, *args, **kwargs):
        jugadora_id = kwargs.pop('jugadora_id', None)
        super(JugadoraDetalleForm, self).__init__(*args, **kwargs)
        
        if jugadora_id:
            # Obtener el historial y personalizarlo para mostrar más información
            historial = JugadoraPorAno.objects.filter(jugadora_id=jugadora_id).order_by('-ano')
            self.fields['historial'].queryset = historial
            self.fields['historial'].label = "Historial por Año"
            
            # Personalizar cómo se muestra cada opción en el select
            self.fields['historial'].label_from_instance = lambda obj: (
                f"Año: {obj.ano} - Categoría: {obj.categoria} - División: {obj.division}"
            )

class FiltroCategoriaDivisionAnoForm(forms.Form):
    ano = forms.ModelChoiceField(
        queryset=JugadoraPorAno.objects.values_list('ano', flat=True).distinct().order_by('ano'),
        label='Año',
        to_field_name='ano'
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        label='Categoría', 
        to_field_name='nombre'  # Usar el campo nombre en lugar del id
    )
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        label='División',
        to_field_name='nombre'  # Usar el campo nombre en lugar del id
    )
    
class EstadoJugadoraForm(forms.ModelForm):
    class Meta:
        model = EstadoJugadora
        fields = ['fecha', 'estadoN', 'posiciones', 'observaciones', ]
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'posiciones': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }