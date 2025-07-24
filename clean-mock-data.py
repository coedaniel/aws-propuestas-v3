#!/usr/bin/env python3
"""
Script para limpiar datos mock de DynamoDB y dejar solo proyectos reales
"""

import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('aws-propuestas-v3-projects-prod')

def list_all_projects():
    """Lista todos los proyectos en la tabla"""
    try:
        response = table.scan()
        projects = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            projects.extend(response.get('Items', []))
        
        return projects
    except Exception as e:
        print(f"Error listing projects: {e}")
        return []

def delete_project(project_id):
    """Elimina un proyecto específico"""
    try:
        table.delete_item(Key={'id': project_id})
        print(f"✅ Deleted project: {project_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting project {project_id}: {e}")
        return False

def is_mock_project(project):
    """Determina si un proyecto es mock data"""
    mock_indicators = [
        "Migracion Cloud Empresa ABC",
        "Setup RDS MySQL", 
        "Arquitectura Serverless E-commerce",
        "VPN Site-to-Site",
        "Sistema de Inventario",
        "Proyecto Test"
    ]
    
    project_name = project.get('name', '')
    
    # Si el nombre coincide con datos mock
    if project_name in mock_indicators:
        return True
    
    # Si no tiene s3Folder (proyectos mock no tienen archivos reales)
    if not project.get('s3Folder'):
        return True
    
    # Si la descripción es muy genérica
    description = project.get('description', '')
    if description in ['Proyecto AWS profesional', 'Implementacion AWS', '']:
        return True
    
    return False

def main():
    print("🧹 LIMPIANDO DATOS MOCK DE DYNAMODB")
    print("=" * 50)
    
    # Listar todos los proyectos
    projects = list_all_projects()
    print(f"📋 Total proyectos encontrados: {len(projects)}")
    
    if not projects:
        print("ℹ️ No hay proyectos en la tabla")
        return
    
    # Identificar proyectos mock
    mock_projects = []
    real_projects = []
    
    for project in projects:
        if is_mock_project(project):
            mock_projects.append(project)
        else:
            real_projects.append(project)
    
    print(f"🎭 Proyectos mock identificados: {len(mock_projects)}")
    print(f"✅ Proyectos reales: {len(real_projects)}")
    
    # Mostrar proyectos mock
    if mock_projects:
        print("\n🎭 PROYECTOS MOCK A ELIMINAR:")
        for i, project in enumerate(mock_projects, 1):
            print(f"   {i}. {project.get('name', 'Sin nombre')} (ID: {project.get('id', 'Sin ID')})")
    
    # Mostrar proyectos reales
    if real_projects:
        print("\n✅ PROYECTOS REALES A MANTENER:")
        for i, project in enumerate(real_projects, 1):
            print(f"   {i}. {project.get('name', 'Sin nombre')} (ID: {project.get('id', 'Sin ID')})")
    
    # Confirmar eliminación
    if mock_projects:
        confirm = input(f"\n¿Eliminar {len(mock_projects)} proyectos mock? (y/N): ")
        
        if confirm.lower() in ['y', 'yes', 'si', 's']:
            print("\n🗑️ Eliminando proyectos mock...")
            
            deleted_count = 0
            for project in mock_projects:
                if delete_project(project.get('id')):
                    deleted_count += 1
            
            print(f"\n✅ Eliminación completada: {deleted_count}/{len(mock_projects)} proyectos eliminados")
            
            # Verificar estado final
            remaining_projects = list_all_projects()
            print(f"📊 Proyectos restantes en tabla: {len(remaining_projects)}")
            
        else:
            print("❌ Eliminación cancelada")
    else:
        print("\nℹ️ No hay proyectos mock para eliminar")

if __name__ == "__main__":
    main()
