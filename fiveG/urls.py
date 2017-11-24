from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^demo', views.displayDemo, name='displayDemo'),
    url(r'^show_normal_col_in_table', views.show_normal_col_in_table, name="show_normal_col_in_table"),
    url(r'^loadMore', views.loadMore, name="loadMore")
]