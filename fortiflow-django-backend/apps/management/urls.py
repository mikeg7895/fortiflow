from django.urls import path
from . import views

urlpatterns = [
    path('programs/', views.ProgramListView.as_view(), name='program-list'),
    path('programs/create/', views.ProgramCreateView.as_view(), name='program-create'),
    path('programs/<int:pk>/edit/', views.ProgramEditView.as_view(), name='program-edit'),
    path('programs/<int:pk>/delete/', views.ProgramDeleteView.as_view(), name='program-delete'),

    # Assignment URLs
    path('assignments/', views.AssignmentListView.as_view(), name='assignment-list'),
    path('assignments/create/', views.AssignmentCreateView.as_view(), name='assignment-create'),
    path('assignments/<int:program_id>/', views.AssignmentListView.as_view(), name='assignment-list-program'),
    path('assignments/create/<int:program_id>/', views.AssignmentCreateView.as_view(), name='assignment-create-program'),
    path('assignments/edit/<int:pk>/', views.AssignmentEditView.as_view(), name='assignment-edit'),
    path('assignments/edit/<int:pk>/<int:program_id>/', views.AssignmentEditView.as_view(), name='assignment-edit-program'),
    path('assignments/delete/<int:pk>/', views.AssignmentDeleteView.as_view(), name='assignment-delete'),

    # Management URLs
    path('managements/<int:assignment_id>/', views.ManagementListView.as_view(), name='management-list'),
    path('managements/create/<int:assignment_id>/', views.ManagementCreateView.as_view(), name='management-create'),
    path('managements/edit/<int:pk>/', views.ManagementEditView.as_view(), name='management-edit'),
    path('managements/delete/<int:pk>/', views.ManagementDeleteView.as_view(), name='management-delete'),
]
