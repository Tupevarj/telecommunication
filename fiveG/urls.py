from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^demo', views.displayDemo, name='displayDemo'),
    url(r'^show_normal_col_in_table', views.show_normal_col_in_table, name="show_normal_col_in_table"),
    url(r'^updateCharts', views.update_charts, name="updateCharts"),
    url(r'^controlPanel', views.controlPanel, name="controlPanel"),
    url(r'^loadNewestDominateMap', views.loadNewestDominateMap, name="loadNewestDominateMap"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)