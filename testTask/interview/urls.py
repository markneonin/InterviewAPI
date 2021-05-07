from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'interview', InterviewView, basename='interview')
router.register(r'answers', Answers, basename='Ans')
urlpatterns = router.urls