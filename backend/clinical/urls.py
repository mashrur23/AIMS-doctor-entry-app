from django.urls import path

from . import views


urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("schema/", views.form_schema, name="form_schema"),
    path("consultations/", views.consultations, name="consultations"),
    path("consultations/<uuid:consultation_id>/", views.consultation_detail, name="consultation_detail"),
    path("consultations/<uuid:consultation_id>/json/", views.consultation_json, name="consultation_json"),
    path("consultations/<uuid:consultation_id>/excel/", views.consultation_excel, name="consultation_excel"),
    path("export/excel/", views.all_consultations_excel, name="all_consultations_excel"),
    path(
        "export/excel/save-to-downloads/",
        views.save_all_consultations_excel_to_downloads,
        name="save_all_consultations_excel_to_downloads",
    ),
]
