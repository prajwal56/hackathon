# rules/urls.py

from rest_framework.routers import DefaultRouter
from .views import RulesViewSet

router = DefaultRouter()
router.register(r'rules', RulesViewSet, basename='rules')

urlpatterns = router.urls
