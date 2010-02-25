#!/usr/bin/bash

echo "Bienvenido al asistente de configuración de Turpial"
echo "==================================================="
echo "Este asistente instalará y configurará todas las dependencias necesarias"
echo "para que Turpial pueda ejecutarse. Presione ENTER para continuar"
echo ""
read X
echo "Actualizando paquetes..."
aptitude -y update
echo "Instalando dependencias..."
aptitude -y install python-simplejson python-gtk2 python-notify python-pygame
echo "Terminado"

