from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update_alarm_gui', views.update_alarm_gui, name="update_alarm_gui"),
    url(r'^update_ml_table', views.update_ml_table, name="update_ml_table"),
    url(r'^updateCharts', views.update_charts, name="updateCharts"),
    url(r'^updateRegressionChart', views.update_reg_chart, name="update_reg_chart"),
    url(r'^saveMLModels', views.save_ml_models, name="save_ml_models"),
    url(r'^loadMLModels', views.load_ml_models, name="load_ml_models"),
    url(r'^controlPanel', views.controlPanel, name="controlPanel"),
    url(r'^selectRegressionModel', views.select_reg_model, name="select_reg_model"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)