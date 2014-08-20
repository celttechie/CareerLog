# This module uses Flask-SuperAdmin to handle the backend.
# todo: add authentication/prevent unauthorized access.
from CareerLog import app, db
from CareerLog.models import Posts, Employment, Education, Certification
from flask_superadmin import Admin
from flask_superadmin import ModelAdmin

admin = Admin(app, name='CareerLog Admin', url='/backend')


# extending classes to change how admin backend handles some collections:
class EmploymentModel(ModelAdmin):

    # This gives the following fields in the list of documents
    list_display = ('position', 'employer', 'start_year', 'start_month')


class EducationModel(ModelAdmin):

    list_display = ('fieldofstudy', 'institution', 'start_year')


class CertificationModel(ModelAdmin):

    list_display = ('certification', 'priority', 'authority',
                    'certified_year', 'certified_month')

admin.register(Employment, EmploymentModel)
admin.register(Posts)
admin.register(Education, EducationModel)
admin.register(Certification, CertificationModel)
