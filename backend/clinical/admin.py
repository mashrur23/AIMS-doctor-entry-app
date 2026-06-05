from django.contrib import admin

from .models import (
    Advice,
    AllergicHistory,
    ChiefComplaint,
    ClinicalExam,
    Consultation,
    Diagnosis,
    FamilyHistory,
    GynaeObsHistory,
    HealthScreening,
    Investigation,
    Medication,
    Patient,
    PersonalHistory,
)


admin.site.register(Patient)
admin.site.register(Consultation)
admin.site.register(FamilyHistory)
admin.site.register(AllergicHistory)
admin.site.register(PersonalHistory)
admin.site.register(GynaeObsHistory)
admin.site.register(ChiefComplaint)
admin.site.register(HealthScreening)
admin.site.register(ClinicalExam)
admin.site.register(Investigation)
admin.site.register(Diagnosis)
admin.site.register(Medication)
admin.site.register(Advice)
