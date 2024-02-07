
from datetime import datetime, timedelta
import queue
from django.db.models import Q

from socios.forms import DisciplinaForm, SociosForm
from socios.helpers import obtener_nombre_del_mes
from socios.models import Factura, Inscripcion, Socios , Disciplinas
from django.shortcuts import get_object_or_404, redirect, render

fecha_actual = datetime.now().month

def lista_socios(request):
    socios = Socios.objects.all()
    return render(request , "lista_socios.html", {'socios': socios})

def alta_socios(request):
    if request.method == 'POST':
        form = SociosForm(request.POST)
        if form.is_valid():
            # obtengo todas las disciplinas creadas hasta el momento
            disciplinas_total = Disciplinas.objects.all()
            print("entreee")
            nuevo_dni = form.cleaned_data['dni']
            nuevo_nro_socio = form.cleaned_data['nroSocio']
            if (Socios.objects.filter(dni = nuevo_dni).exists()):
                print("numero dni")
                form.add_error('dni', 'el dni ya se encuentra registrado')
                return render(request, 'alta_socios.html', {'form': form , 'disciplinas':disciplinas_total})
            else:
                if (Socios.objects.filter(nroSocio = nuevo_nro_socio).exists()):
                    print("numero socio")
                    form.add_error('nroSocio', 'el numero de socio ya se encuentra registrado')
                    return render(request, 'alta_socios.html', {'form': form , 'disciplinas':disciplinas_total})
                else:
                    nuevo_socio = form.save(commit=False)
                    disciplinas_seleccionadas = form.cleaned_data['disciplinas']
                    nuevo_socio.save()
                    Socios.objects.filter(dni=nuevo_dni).update(fecha_ingreso = datetime.now().date(),)
                    for disciplina in disciplinas_seleccionadas.all():
                        if datetime.now().day >= 28:
                            fecha_reinicio = datetime.now() + timedelta(days=28)
                        else:    
                            fecha_reinicio = datetime.now() + timedelta(days=30)
                        
                        Inscripcion.objects.create(socio=nuevo_socio, disciplina=disciplina, fecha_reinicio=fecha_reinicio)
                    
                    form.save_m2m()
                    return redirect('lista_socios')      
    else:
        form = SociosForm()
        disciplinas = Disciplinas.objects.all()

    return render(request, 'alta_socios.html', {'form': form , 'disciplinas':disciplinas})

def eliminar_socio(request , id_socio):
    socio = Socios.objects.get(id = id_socio)
    Inscripcion.objects.filter(socio=socio).delete()
    socio.disciplinas.clear()
    socio.delete()
    return redirect('lista_socios')

def modificar_socio(request, id_socio):
    socio = get_object_or_404(Socios, id=id_socio)
    disciplinas = Disciplinas.objects.all()

    if request.method == 'POST':
        form = SociosForm(request.POST, instance=socio)
        if form.is_valid():
            socio = form.save(commit=False)
            socio.dni = request.POST['dni']
            socio.nroSocio = request.POST['nroSocio']
            socio.nombre = request.POST['nombre']
            socio.apellido = request.POST['apellido']
            socio.tipo_socio = request.POST['tipo_socio']
            socio.save()
            disciplinas_existentes = Inscripcion.objects.filter(socio=socio)
            print("existentes" , disciplinas_existentes)
            disciplinas_seleccionadas = form.cleaned_data['disciplinas']
            print("seleccionadas" , disciplinas_seleccionadas)

            for disciplina_seleccionada in disciplinas_seleccionadas:
                disciplina_existente = disciplinas_existentes.filter(disciplina=disciplina_seleccionada).first()

                if disciplina_existente is None:
                    if datetime.now().day >= 28:
                        fecha_reinicio = datetime.now() + timedelta(days=28)
                    else:
                        fecha_reinicio = datetime.now() + timedelta(days=30)

                    Inscripcion.objects.create(socio=socio, disciplina=disciplina_seleccionada, fecha_reinicio=fecha_reinicio)


            form.save_m2m()
            return redirect('lista_socios')      

    else:
        form = SociosForm(instance=socio)
        form.fields['dni'].widget.attrs['readonly'] = True
        form.fields['nroSocio'].widget.attrs['readonly'] = True
        form.fields['nombre'].widget.attrs['readonly'] = True
        form.fields['apellido'].widget.attrs['readonly'] = True
        form.fields['disciplinas'].label = ''
        form.fields['disciplinas'].choices = [
            (c.pk, c.nombre) for c in disciplinas]
        form.initial['disciplinas'] = [disciplina.pk for disciplina in socio.disciplinas.all()]

    return render(request, 'alta_socios.html', {'form': form, 'disciplinas': disciplinas})


def lista_disciplinas(request):
    disciplinas = Disciplinas.objects.all()
    return render(request , "lista_disciplinas.html", {'disciplinas': disciplinas})

def alta_disciplina(request):
    if request.method == "POST":
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            nuevo_nombre = form.cleaned_data['nombre']
            if (Disciplinas.objects.filter(nombre = nuevo_nombre).exists()):
                form.add_error('nombre', 'el nombre de esta disciplina ya se encuentra registrado')
                return render(request, 'alta_disciplina.html', {'form': form})
            form.save()
            return redirect('lista_disciplinas')
    else:
        form = DisciplinaForm()
    return render(request, "alta_disciplina.html", {"form": form})


def eliminar_disciplina(request , id_disciplina):
    disciplina = Disciplinas.objects.get(id = id_disciplina)
    socios_con_disciplina = Socios.objects.filter(disciplinas=disciplina)
    for socio in socios_con_disciplina:
        socio.disciplinas.remove(disciplina)
    disciplina.delete()
    return redirect('lista_disciplinas')

def modificar_disciplina(request , id_disciplina):
    disciplina = get_object_or_404(Disciplinas, id = id_disciplina)
    if request.method == "POST":
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            disciplina = form.save(commit=False)
            disciplina.monto_afiliado = request.POST['monto_afiliado']
            disciplina.monto_adherente = request.POST['monto_adherente']
            disciplina.save()
            form.save()
            return redirect('lista_disciplinas')
    else:
        form = DisciplinaForm(instance=disciplina)
        form.fields['nombre'].widget.attrs['readonly'] = True

    return render(request, "alta_disciplina.html", {"form": form})

# preparo los elementos a mostrar en la vista de "PAGAR" de un socio
def facturacion(request , id_socio):
    reiniciar_pagos_para_nuevo_mes()
    mes_actual = datetime.now().month
    nombre_mes = obtener_nombre_del_mes(mes_actual)
    socio = Socios.objects.get(id = id_socio) 
    # obtengo disciplinas pendieites a pagar
    disciplinas_inscripcion_pendientes = obtener_disciplinas_pendientes(id_socio)
    # obtengo las disciplinas ya pagas del mes
    disciplinas_inscripcion_pagadas = obtener_disciplinas_pagadas(id_socio)
    # obtengo las disciplinas q no fueron pagadas aun
    facturas_vencidas=Factura.objects.filter(socio = id_socio , pagado = False)
    return render(request, "facturacion.html" ,
                {'socio':socio ,
                "disciplinas_sin_pagar":disciplinas_inscripcion_pendientes,
                "disciplinas_pagadas": disciplinas_inscripcion_pagadas,
                "facturas_vencidas": facturas_vencidas,
                "mes":nombre_mes,
                })

# se establece el pago entre una disciplina y el socio. tambien se crea una factura
def pagar(request , socio_id , disciplina_id):
    socio = Socios.objects.get(id=socio_id)
    disciplina_a_pagar = Disciplinas.objects.get(id=disciplina_id)

    if socio.tipo_socio == Socios.socio_afiliado:
        monto_pagado = disciplina_a_pagar.monto_afiliado
    else:
        monto_pagado = disciplina_a_pagar.monto_adherente

    nueva_factura = Factura.objects.create(
        socio=socio,
        disciplina=disciplina_a_pagar,
        monto_total=monto_pagado,
        fecha_pago = datetime.now().date(),
        pagado = True
    )
    nueva_factura.save()
    inscripcion =  Inscripcion.objects.get(socio_id = socio_id , disciplina_id = disciplina_id)
    inscripcion.marcar_como_pagado()
    return redirect('facturacion', id_socio=socio_id)

# se paga una factura que estaba vencida actualizando su campo de fecha y de pago
def pagar_vencidos(request , factura_id):
    factura=Factura.objects.get(id=factura_id)
    socio = Socios.objects.get(id=factura.socio.pk)
    Factura.objects.filter(id=factura_id).update(fecha_pago = datetime.now() , pagado = True)
    return redirect('facturacion', id_socio=socio.pk)

    

#reinicia las disciplinas para poder pagarlas en el nuevo mes
@staticmethod
def reiniciar_pagos_para_nuevo_mes():
    dia_actual = datetime.now().day
    mes_actual = datetime.now().month
    # obtengo todas las disciplinas
    inscripciones = Inscripcion.objects.all()
    if inscripciones.exists():
        #por cada inscripcion verifico el mes de reinicio con el mes actual
        for inscripcion in inscripciones:
            if inscripcion.fecha_reinicio.month == mes_actual:
                #verificacion de dia por si hubo un dia feriado
                if dia_actual >= inscripcion.fecha_reinicio.day:
                    hoy = datetime.now()
                    if hoy.day >=28:
                        reinicio = datetime(hoy.year, hoy.month, hoy.day) + timedelta(days=28 )
                    else:
                        reinicio = datetime(hoy.year, hoy.month, hoy.day) + timedelta(days=30)
                        
                    if inscripcion.pagado == False:
                        marcar_facturas_vencidas(inscripcion.socio.pk , inscripcion.disciplina,
                                                inscripcion.disciplina.monto_adherente ,inscripcion.disciplina.monto_afiliado ,
                                                inscripcion.fecha_reinicio)
                        inscripcion.fecha_reinicio = reinicio
                        inscripcion.save()
                    else:
                        inscripcion.pagado=False
                        inscripcion.fecha_pago=None
                        inscripcion.fecha_reinicio = reinicio
                        inscripcion.save()
                        # Inscripcion.objects.filter(pagado=True, fecha_reinicio__month=mes_actual).update(pagado=False, fecha_pago=None)


# crea una nueva factura vencida perteneciente a un socio
def marcar_facturas_vencidas(socio , disciplina, adherente,afiliado,reinicio):
    # busca la persona por su id
    persona = Socios.objects.get(id = socio)
    if persona.tipo_socio == Socios.socio_afiliado:
        monto_pagado = afiliado
    else:
        monto_pagado = adherente
    nueva_factura = Factura.objects.create(
    socio=persona,
    disciplina=disciplina,
    monto_total=monto_pagado,
    fecha_vencido = reinicio
    )
    nueva_factura.save()
    
            
        

#devuelve las disciplinas del socio que aun faltan pagar
def obtener_disciplinas_pendientes(socio_id):
    disciplinas_pendientes = Inscripcion.objects.filter(pagado=False , socio = socio_id)
    return disciplinas_pendientes

def obtener_disciplinas_pagadas(socio_id):
    disciplinas_pendientes = Inscripcion.objects.filter(pagado=True , socio = socio_id)
    return disciplinas_pendientes

def detalle_factura(request,factura_id):
    factura = Factura.objects.get(id = factura_id)
    socio = Socios.objects.get(id = factura.socio.pk)
    disciplina = Disciplinas.objects.get(id = factura.disciplina.pk)
    if socio.tipo_socio == Socios.socio_afiliado:
        monto_pagado = disciplina.monto_afiliado
    else:
        monto_pagado = disciplina.monto_adherente
    return render(request, "detalle_factura.html" ,
                {'socio':socio ,
                "disciplina":disciplina,
                "monto": monto_pagado,
                "factura": factura,
                })
    
    
def listado_facturas_socio(request, socio_id):
    facturas = Factura.objects.filter(socio_id = socio_id , pagado = True)
    socio = Socios.objects.get(id = socio_id)
    return render(request, "lista_facturas_socio.html",{"socio":socio , "facturas":facturas})

def listado_facturas(request):
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            facturas = Factura.objects.filter(
                Q(fecha_pago__gte=fecha_inicio) &
                Q(fecha_pago__lte=fecha_fin) &
                Q(pagado=True)
            )
            return render(request, "listado_facturas.html", {"facturas": facturas})
        else:
            if fecha_inicio and not fecha_fin:
                facturas = Factura.objects.filter(
                    Q(fecha_pago__gte=fecha_inicio) &
                    Q(pagado=True)
                    )
                return render(request, "listado_facturas.html", {"facturas": facturas})
            else:
                 if not fecha_inicio and fecha_fin:
                    facturas = Factura.objects.filter(
                        Q(fecha_pago__lte=fecha_fin) &
                        Q(pagado=True)
                            )
                    return render(request, "listado_facturas.html", {"facturas": facturas})
    
    facturas= Factura.objects.filter(pagado=True)
    return render(request, "listado_facturas.html", {"facturas": facturas})
    
    
# MAIN PARA EL EJECUTABLE 
    
if __name__ == "__main__":
    lista_socios()