#!/bin/bash
# cleanup.sh - Script para limpiar archivos innecesarios

echo "Limpiando archivos temporales y de desarrollo..."

# Eliminar archivos temporales
find . -name "*.tmp" -type f -delete
find . -name "*.bak" -type f -delete
find . -name ".DS_Store" -type f -delete

# Eliminar directorios de desarrollo
rm -rf .next/cache
rm -rf node_modules/.cache

echo "Limpieza completada."
