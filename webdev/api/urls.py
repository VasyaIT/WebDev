from django.urls import path
from .channels import views as c_views
from .users import views as u_views
from .payments import views as p_views


urlpatterns = [
    path('channels/', c_views.ChannelListAPI.as_view(), name='api_channels_list'),
    path('channels/create/', c_views.ChannelCreateAPI.as_view(), name='api_channels_create'),
    path('channels/update/', c_views.ChannelUpdateAPI.as_view(), name='api_channels_update'),
    path('channels/delete/', c_views.ChannelDeleteAPI.as_view(), name='api_channels_delete'),
    path('channels/<slug>/', c_views.ChannelRetrieveAPI.as_view(), name='api_channels_detail'),
    path('tag/<slug:tag_slug>/', c_views.ChannelListAPI.as_view(), name='api_detail_tag'),
]
