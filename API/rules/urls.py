# rules/urls.py

from rest_framework.routers import DefaultRouter
from .views import RulesViewSet

router = DefaultRouter()
router.register(r'', RulesViewSet, basename='')

urlpatterns = router.urls
