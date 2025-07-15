"""
MCP Server - S3 Upload Management
Handles uploading generated documents to S3 with proper organization
"""

import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
import base64

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Upload generated documents to S3"""
    try:
        project_info = event.get('project_info', {})
        documents = event.get('documents', {})
        bucket_name = event.get('bucket_name', '')
        
        print(f"Uploading documents for project: {project_info.get('name', 'Unknown')}")
        
        # Upload all documents
        upload_results = upload_documents_to_s3(
            documents, 
            bucket_name, 
            project_info
        )
        
        return {
            'upload_results': upload_results,
            'uploaded_at': datetime.now().isoformat(),
            'project_name': project_info.get('name', 'AWS Project'),
            'bucket_name': bucket_name
        }
        
    except Exception as e:
        print(f"Error in S3 upload: {str(e)}")
        return {'error': str(e)}

def upload_documents_to_s3(documents: Dict[str, Any], bucket_name: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Upload all generated documents to S3 with organized structure"""
    
    project_name = project_info.get('name', 'AWS Project').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    project_folder = f"propuestas/{project_name}_{timestamp}"
    
    upload_results = {
        'project_folder': project_folder,
        'uploaded_files': [],
        'public_urls': [],
        'errors': []
    }
    
    try:
        # Create project metadata file
        metadata = {
            'project_name': project_info.get('name', 'AWS Project'),
            'solution_type': project_info.get('solution_type', 'integral'),
            'generated_at': datetime.now().isoformat(),
            'documents_included': list(documents.keys())
        }
        
        metadata_key = f"{project_folder}/project_metadata.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2),
            ContentType='application/json'
        )
        
        upload_results['uploaded_files'].append(metadata_key)
        upload_results['public_urls'].append(f"https://{bucket_name}.s3.amazonaws.com/{metadata_key}")
        
        # Upload each document type
        for doc_type, doc_data in documents.items():
            try:
                if doc_type == 'word_document':
                    _upload_word_document(doc_data, bucket_name, project_folder, upload_results)
                elif doc_type == 'csv_activities':
                    _upload_csv_document(doc_data, bucket_name, project_folder, upload_results)
                elif doc_type == 'cloudformation_template':
                    _upload_cloudformation_template(doc_data, bucket_name, project_folder, upload_results)
                elif doc_type == 'cost_analysis':
                    _upload_cost_analysis(doc_data, bucket_name, project_folder, upload_results)
                elif doc_type == 'diagrams':
                    _upload_diagrams(doc_data, bucket_name, project_folder, upload_results)
                    
            except Exception as e:
                error_msg = f"Error uploading {doc_type}: {str(e)}"
                print(error_msg)
                upload_results['errors'].append(error_msg)
        
        # Create index.html for easy access
        _create_project_index(bucket_name, project_folder, upload_results, project_info)
        
    except Exception as e:
        error_msg = f"Error in S3 upload process: {str(e)}"
        print(error_msg)
        upload_results['errors'].append(error_msg)
    
    return upload_results

def _upload_word_document(doc_data: Dict[str, Any], bucket_name: str, project_folder: str, upload_results: Dict[str, Any]):
    """Upload Word document to S3"""
    
    if 'content' in doc_data and 'filename' in doc_data:
        key = f"{project_folder}/documents/{doc_data['filename']}"
        
        # If content is base64 encoded, decode it
        if isinstance(doc_data['content'], str):
            try:
                content = base64.b64decode(doc_data['content'])
            except:
                content = doc_data['content'].encode('utf-8')
        else:
            content = doc_data['content']
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content,
            ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        upload_results['uploaded_files'].append(key)
        upload_results['public_urls'].append(f"https://{bucket_name}.s3.amazonaws.com/{key}")

def _upload_csv_document(doc_data: Dict[str, Any], bucket_name: str, project_folder: str, upload_results: Dict[str, Any]):
    """Upload CSV document to S3"""
    
    if 'content' in doc_data and 'filename' in doc_data:
        key = f"{project_folder}/documents/{doc_data['filename']}"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=doc_data['content'],
            ContentType='text/csv'
        )
        
        upload_results['uploaded_files'].append(key)
        upload_results['public_urls'].append(f"https://{bucket_name}.s3.amazonaws.com/{key}")

def _upload_cloudformation_template(doc_data: Dict[str, Any], bucket_name: str, project_folder: str, upload_results: Dict[str, Any]):
    """Upload CloudFormation template to S3"""
    
    if 'content' in doc_data and 'filename' in doc_data:
        key = f"{project_folder}/infrastructure/{doc_data['filename']}"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=doc_data['content'],
            ContentType='application/x-yaml'
        )
        
        upload_results['uploaded_files'].append(key)
        upload_results['public_urls'].append(f"https://{bucket_name}.s3.amazonaws.com/{key}")

def _upload_cost_analysis(doc_data: Dict[str, Any], bucket_name: str, project_folder: str, upload_results: Dict[str, Any]):
    """Upload cost analysis to S3"""
    
    if 'content' in doc_data and 'filename' in doc_data:
        key = f"{project_folder}/analysis/{doc_data['filename']}"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=doc_data['content'],
            ContentType='text/csv'
        )
        
        upload_results['uploaded_files'].append(key)
        upload_results['public_urls'].append(f"https://{bucket_name}.s3.amazonaws.com/{key}")

def _upload_diagrams(doc_data: Dict[str, Any], bucket_name: str, project_folder: str, upload_results: Dict[str, Any]):
    """Upload architecture diagrams to S3"""
    
    if isinstance(doc_data, dict) and 'diagrams' in doc_data:
        for diagram_type, diagram_info in doc_data['diagrams'].items():
            if 'content' in diagram_info and 'filename' in diagram_info:
                key = f"{project_folder}/diagrams/{diagram_info['filename']}"
                
                # Decode base64 image content
                try:
                    content = base64.b64decode(diagram_info['content'])
                except:
                    content = diagram_info['content']
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=content,
                    ContentType='image/png'
                )
                
                upload_results['uploaded_files'].append(key)
                upload_results['public_urls'].append(f"https://{bucket_name}.s3.amazonaws.com/{key}")

def _create_project_index(bucket_name: str, project_folder: str, upload_results: Dict[str, Any], project_info: Dict[str, Any]):
    """Create an HTML index page for easy access to all documents"""
    
    project_name = project_info.get('name', 'AWS Project')
    solution_type = project_info.get('solution_type', 'integral')
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Propuesta AWS - {project_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #FF9900;
        }}
        .header h1 {{
            color: #232F3E;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            font-size: 18px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #232F3E;
            border-left: 4px solid #FF9900;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .file-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .file-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            transition: transform 0.2s;
        }}
        .file-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .file-card h3 {{
            color: #232F3E;
            margin-top: 0;
            margin-bottom: 10px;
        }}
        .file-card p {{
            color: #666;
            margin-bottom: 15px;
        }}
        .download-btn {{
            display: inline-block;
            background: #FF9900;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.2s;
        }}
        .download-btn:hover {{
            background: #e88b00;
        }}
        .info-box {{
            background: #e8f4fd;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Propuesta AWS: {project_name}</h1>
            <p>Tipo de Solución: {solution_type.replace('_', ' ').title()}</p>
            <p>Generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
        </div>

        <div class="info-box">
            <strong>📋 Contenido de la Propuesta:</strong><br>
            Esta propuesta incluye documentación técnica completa, análisis de costos, 
            plantillas de infraestructura y diagramas de arquitectura para su proyecto AWS.
        </div>

        <div class="section">
            <h2>📄 Documentos Principales</h2>
            <div class="file-grid">"""
    
    # Add document cards based on uploaded files
    for file_path in upload_results['uploaded_files']:
        filename = file_path.split('/')[-1]
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_path}"
        
        if filename.endswith('.docx'):
            html_content += f"""
                <div class="file-card">
                    <h3>📄 Documento Principal</h3>
                    <p>Propuesta técnica completa con especificaciones detalladas</p>
                    <a href="{file_url}" class="download-btn" download>Descargar Word</a>
                </div>"""
        elif filename.endswith('.csv') and 'activities' in filename.lower():
            html_content += f"""
                <div class="file-card">
                    <h3>📋 Plan de Actividades</h3>
                    <p>Cronograma detallado de implementación del proyecto</p>
                    <a href="{file_url}" class="download-btn" download>Descargar CSV</a>
                </div>"""
        elif filename.endswith('.csv') and 'cost' in filename.lower():
            html_content += f"""
                <div class="file-card">
                    <h3>💰 Análisis de Costos</h3>
                    <p>Estimación detallada de costos mensuales y anuales</p>
                    <a href="{file_url}" class="download-btn" download>Descargar CSV</a>
                </div>"""
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            html_content += f"""
                <div class="file-card">
                    <h3>🏗️ Plantilla CloudFormation</h3>
                    <p>Infraestructura como código para despliegue automatizado</p>
                    <a href="{file_url}" class="download-btn" download>Descargar YAML</a>
                </div>"""
        elif filename.endswith('.png') and 'diagram' in filename.lower():
            html_content += f"""
                <div class="file-card">
                    <h3>🏛️ Diagrama de Arquitectura</h3>
                    <p>Representación visual de la arquitectura propuesta</p>
                    <a href="{file_url}" class="download-btn" target="_blank">Ver Diagrama</a>
                </div>"""
    
    html_content += f"""
            </div>
        </div>

        <div class="section">
            <h2>🔗 Enlaces Útiles</h2>
            <div class="file-grid">
                <div class="file-card">
                    <h3>🧮 Calculadora de Precios AWS</h3>
                    <p>Herramienta oficial para estimar costos personalizados</p>
                    <a href="https://calculator.aws" class="download-btn" target="_blank">Abrir Calculadora</a>
                </div>
                <div class="file-card">
                    <h3>📚 Documentación AWS</h3>
                    <p>Documentación técnica oficial de los servicios AWS</p>
                    <a href="https://docs.aws.amazon.com" class="download-btn" target="_blank">Ver Documentación</a>
                </div>
                <div class="file-card">
                    <h3>🎓 AWS Training</h3>
                    <p>Recursos de capacitación y certificación AWS</p>
                    <a href="https://aws.amazon.com/training" class="download-btn" target="_blank">Ver Cursos</a>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Propuesta generada por AWS Propuestas V3 - Sistema de Consultoría Arquitectónica</p>
            <p>Para consultas adicionales, contacte a su arquitecto de soluciones AWS</p>
        </div>
    </div>
</body>
</html>"""
    
    # Upload the index.html file
    index_key = f"{project_folder}/index.html"
    s3_client.put_object(
        Bucket=bucket_name,
        Key=index_key,
        Body=html_content,
        ContentType='text/html'
    )
    
    upload_results['uploaded_files'].append(index_key)
    upload_results['public_urls'].append(f"https://{bucket_name}.s3.amazonaws.com/{index_key}")
    upload_results['index_url'] = f"https://{bucket_name}.s3.amazonaws.com/{index_key}"

def create_s3_bucket_if_not_exists(bucket_name: str, region: str = 'us-east-1') -> bool:
    """Create S3 bucket if it doesn't exist"""
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists")
        return True
        
    except s3_client.exceptions.NoSuchBucket:
        try:
            # Create bucket
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            # Configure bucket for public read access
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            # Configure lifecycle policy
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'PropuestasLifecycle',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': 'propuestas/'},
                        'Transitions': [
                            {
                                'Days': 30,
                                'StorageClass': 'STANDARD_IA'
                            },
                            {
                                'Days': 90,
                                'StorageClass': 'GLACIER'
                            }
                        ]
                    }
                ]
            }
            
            s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            
            print(f"Created bucket {bucket_name} successfully")
            return True
            
        except Exception as e:
            print(f"Error creating bucket {bucket_name}: {str(e)}")
            return False
    
    except Exception as e:
        print(f"Error checking bucket {bucket_name}: {str(e)}")
        return False
