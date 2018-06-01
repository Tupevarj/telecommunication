from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update_alarm_gui', views.update_alarm_gui, name="update_alarm_gui"),
    url(r'^updateCharts', views.update_charts, name="updateCharts"),
    url(r'^createModels', views.create_ml_models, name="create_ml_models"),
    url(r'^saveMLModels', views.save_ml_models, name="save_ml_models"),
    url(r'^loadMLModels', views.load_ml_models, name="load_ml_models"),
    url(r'^startSimulation', views.start_simulation, name="start_simulation"),
    url(r'^startTrainingSimulation', views.start_training_simulation, name="start_training_simulation"),
    url(r'^stopSimulation', views.stop_simulation, name="stop_simulation"),
    #url(r'^controlPanel', views.controlPanel, name="controlPanel"),
    url(r'^controlPanelInput', views.control_panel_input, name="controlPanelInput"),
    url(r'^selectRegressionModel', views.select_reg_model, name="select_reg_model"),
    url(r'^userLocationHistory', views.get_ue_location_history, name="get_ue_location_history"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)