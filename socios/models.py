from datetime import datetime, timedelta
from django.db import models

# Create your models here.

class Disciplinas(models.Model):
    nombre = models.CharField(max_length=100)
    monto_afiliado = models.IntegerField()
    monto_adherente = models.IntegerField()

    def __str__(self):
        return f"{self.nombre}, {self.monto_afiliado}, {self.monto_adherente}"

    def obtener_disciplinas_no_pagadas_mes_anterior(self):
        mes_anterior = datetime.now().date().replace(day=1) - timedelta(days=1)
        disciplinas_no_pagadas = self.inscripcion_set.filter(
            pagado=False,
            fecha_pago__lt=mes_anterior
        )
        return disciplinas_no_pagadas
    
    def obtener_vencimiento(self , socio ):
        inscripcion = Inscripcion.objects.get(socio = socio ,disciplina = self.nombre)
        return inscripcion.fecha_reinicio



class Inscripcion(models.Model):
    socio = models.ForeignKey('Socios', on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    fecha_reinicio = models.DateField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.socio.nombre} - {self.disciplina.nombre} - Pagado: {self.pagado}"

    # se marca la disciplina a pagar y se reinicia su fecha de vencimiento 1 mes mas
    def marcar_como_pagado(self):
        self.pagado = True
        self.fecha_pago = datetime.now().date()   
    # Obtener el primer día del próximo mes
        primer_dia_siguiente_mes = datetime(self.fecha_pago.year, self.fecha_pago.month, 1) + timedelta(days=31 ) 
    # Establecer el día en 5
        # dia = self.fecha_reinicio.day
        # if dia >=28:
        #     self.fecha_reinicio = datetime(primer_dia_siguiente_mes.year, primer_dia_siguiente_mes.month, 28).date()
        # else:
        #     self.fecha_reinicio = datetime(primer_dia_siguiente_mes.year, primer_dia_siguiente_mes.month, dia).date() + timedelta(days=30 )
            
        self.save()


class Socios(models.Model):
    socio_afiliado = 0
    socio_adherente = 1
    tipo = [
        (socio_afiliado, "Afiliado"),
        (socio_adherente, "Adherente")
    ]

    nroSocio = models.IntegerField()
    dni = models.IntegerField()
    apellido = models.CharField(max_length=200, blank=True)
    nombre = models.CharField(max_length=200, blank=True)
    tipo_socio = models.PositiveSmallIntegerField(choices=tipo)
    disciplinas = models.ManyToManyField(Disciplinas, through='Inscripcion')
    fecha_ingreso = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Factura(models.Model):
    socio = models.ForeignKey(Socios, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    monto_total = models.IntegerField()
    fecha_pago = models.DateField(null=True, blank=True)
    fecha_vencido = models.DateField(null=True, blank=True)
    pagado = models.BooleanField(default=False)

    def pagar_factura(self):
        self.pagado = True
        self.fecha_pago = datetime.now().date()
        self.save()
    
    def obtener_nombre_del_mes(self):
        numero_mes = self.fecha_vencido.month
        print(numero_mes)
        try:
            meses = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre"
        }
            return str(self.fecha_vencido.day) +"-"+meses[numero_mes] +"-"+ str(self.fecha_vencido.year)
        except IndexError:
            return "Mes no válido"