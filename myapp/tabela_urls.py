from django.urls import path

from .views2 import (
    homepage_view2, 
    ask_known1_view2, 
    ask_known2_view2, 
    process_values_view2, 
    error_value_view2, 
    error_type_view7
)

urlpatterns = [
    path('', homepage_view2, name='homepage2'),  # Rota para a homepage da "tabela/"
    
    path('tabela1/', ask_known1_view2, name='ask_known1_2'),
    path('tabela2/', ask_known2_view2, name='ask_known2_2'),
    path('tabela3/', process_values_view2, name='process_values_2'),
    
    path('error-value2/', error_value_view2, name='error_value_2'),
    
    path('error-type2/', error_type_view7, name='error_type_7'),
]