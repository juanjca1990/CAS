

from django import forms
from django.forms import CheckboxSelectMultiple, ModelForm, MultipleChoiceField

from socios.models import Disciplinas, Socios

class SociosForm(forms.ModelForm):
    disciplinas = forms.ModelMultipleChoiceField(
        queryset=Disciplinas.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    
    class Meta:
        model = Socios
        fields = ['nroSocio', 'dni', 'apellido', 'nombre', 'tipo_socio', 'disciplinas']
        widgets = {
            'dni': forms.TextInput(attrs={'novalidate': 'novalidate'}),
        }
        

    def __init__(self, *args, **kwargs):
        super(SociosForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control input-text'})
        self.fields['apellido'].widget.attrs.update({'class': 'form-control input-text'})
        self.fields['dni'].widget.attrs.update({'class': 'form-control input-text', 'min':'0'})
        self.fields['nroSocio'].widget.attrs.update({'class':'form-control nro-socio'})
        self.fields['tipo_socio'].widget.attrs.update({'class': 'form-control tipo-socio'})
        self.fields['disciplinas'].widget.attrs.update({'class': 'check-disciplinas'})
        self.fields['disciplinas'].choices = [(c.pk, c.nombre) for c in Disciplinas.objects.all()]
                
                
class DisciplinaForm(ModelForm):
    class Meta:
        model = Disciplinas
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(DisciplinaForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control input-text'})
        self.fields['monto_afiliado'].widget.attrs.update({'class': 'form-control input-monto' ,'min':'0'})
        self.fields['monto_adherente'].widget.attrs.update({'class': 'form-control input-monto' ,'min':'0'})
        