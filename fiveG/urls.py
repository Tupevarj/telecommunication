from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^updateCharts',             views.send_command_to_simulator_module),
    url(r'^startSimulation',          views.send_command_to_simulator_module),
    url(r'^startTrainingSimulation',  views.send_command_to_simulator_module),
    url(r'^stopSimulation',           views.send_command_to_simulator_module),
    url(r'^outageInput',              views.send_command_to_simulator_module),
    url(r'^userLocationHistory',      views.send_command_to_simulator_module),
    url(r'^usersLocationHistoryCell', views.send_command_to_simulator_module),      # Not implemented!
    url(r'^update_alarm_gui',         views.send_command_to_cod_module),
    url(r'^createModels',             views.send_command_to_cod_module),
    url(r'^saveMLModels',             views.send_command_to_cod_module),
    url(r'^loadMLModels',             views.send_command_to_cod_module),
    url(r'^selectRegressionModel',    views.send_command_to_cod_module),
    #url(r'^controlPanel', views.controlPanel, name="controlPanel"),
    url(r'^controlPanelInput', views.control_panel_input, name="controlPanelInput"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)