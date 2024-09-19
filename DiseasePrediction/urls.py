from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path("User.html", views.User, name="User"),
	       path("index.html", views.Logout, name="Logout"),
	       path("Register.html", views.Register, name="Register"),
	       path("UserLogin", views.UserLogin, name="UserLogin"),
	       path("Signup", views.Signup, name="Signup"),
	       path("ChatData", views.ChatData, name="ChatData"),
	       path("DiseaseInfo.html", views.DiseaseInfo, name="DiseaseInfo"),
	       path("DiseaseInfoAction", views.DiseaseInfoAction, name="DiseaseInfoAction"),
	       path("ChatBotPage", views.ChatBotPage, name="ChatBotPage"),
	       path("BookAppointment.html", views.BookAppointment, name="BookAppointment"),
	       path("BookAppointmentAction", views.BookAppointmentAction, name="BookAppointmentAction"),
]
