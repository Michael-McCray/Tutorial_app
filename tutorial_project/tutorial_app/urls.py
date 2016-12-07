from django.conf.urls import patterns, url 
from tutorial_app import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
    url(r'^add-category/', views.add_category, name="add-category"),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add-page/$', views.add_page, name='add-page'),
    url(r'^register/', views.register, name='register'),
    url(r'^login/', views.user_login, name='login'),
    url(r'^logout/', views.user_logout, name='logout'),
    url(r'^goto/$', views.track_url, name='goto'),
    url(r'^user/(?P<user_username>[\w\-]+)/$', views.user_profile, name='profile'),
    url(r'^user/(?P<user_username>[\w\-]+)/edit/$', views.edit_profile, name='edit_profile'),
    url(r'^contact/', views.contact, name='contact'),
    url(r'^like_category/$', views.like_category, name='like_category'),
    url(r'^suggest_category/$', views.suggest_category, name='suggest_category'),
    url(r'^auto_add_page/$', views.auto_page_add, name='auto-add'),
    )

