#!/usr/bin/env python3
"""
Script de diagnóstico para verificar usuarios y tenants en FortiFlow
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/workspace/fortiflow-django-backend')
django.setup()

from apps.account.models import CustomUser, Tenant

def main():
    print("=== DIAGNÓSTICO DE USUARIOS Y TENANTS ===\n")
    
    # Verificar usuarios
    users = CustomUser.objects.all()
    users_without_tenant = CustomUser.objects.filter(tenant__isnull=True)
    
    print(f"Total de usuarios: {users.count()}")
    print(f"Usuarios sin tenant: {users_without_tenant.count()}")
    
    if users_without_tenant.exists():
        print("\nUsuarios sin tenant asignado:")
        for user in users_without_tenant:
            print(f"  - {user.username} (ID: {user.id})")
    
    # Verificar tenants
    tenants = Tenant.objects.all()
    print(f"\nTotal de tenants: {tenants.count()}")
    
    if tenants.exists():
        print("Tenants disponibles:")
        for tenant in tenants:
            user_count = CustomUser.objects.filter(tenant=tenant).count()
            print(f"  - {tenant.name} (ID: {tenant.id}) - {user_count} usuarios")
    
    # Sugerir soluciones
    if users_without_tenant.exists():
        print("\n=== SOLUCIONES SUGERIDAS ===")
        if tenants.exists():
            default_tenant = tenants.first()
            print(f"1. Asignar todos los usuarios sin tenant al tenant '{default_tenant.name}':")
            print(f"   users_without_tenant.update(tenant_id={default_tenant.id})")
        else:
            print("1. Crear un tenant por defecto:")
            print("   tenant = Tenant.objects.create(name='Default Organization')")
            print("   users_without_tenant.update(tenant=tenant)")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    main()
