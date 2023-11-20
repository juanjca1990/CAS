from django.contrib import admin
from django.urls import path

from socios import views

urlpatterns = [
    path('alta_socios/', views.alta_socios, name="alta_socios"),
    path('eliminar_socio/<id_socio>', views.eliminar_socio, name="eliminar_socio"), 
    path('modificar_socio/<id_socio>', views.modificar_socio, name="modificar_socio"),
    
    path('alta_disciplina/', views.alta_disciplina, name="alta_disciplina"), 
    path('lista_disciplinas/', views.lista_disciplinas, name="lista_disciplinas"), 
    path('eliminar_disciplina/<id_disciplina>', views.eliminar_disciplina, name="eliminar_disciplina"),
    path('modificar_disciplina/<id_disciplina>', views.modificar_disciplina, name="modificar_disciplina"),
    
    path('facturacion/<id_socio>', views.facturacion, name="facturacion"),
    path('pagar/<socio_id>,<disciplina_id>', views.pagar, name="pagar"),
    path('pagar_vencidos/<factura_id>', views.pagar_vencidos, name="pagar_vencidos"),
    path('detalle_factura/<factura_id>', views.detalle_factura, name="detalle_factura"),
    path('listado_facturas_socio/<socio_id>', views.listado_facturas_socio, name="listado_facturas_socio"),  
    path('listado_facturas/', views.listado_facturas, name="listado_facturas"),    
]