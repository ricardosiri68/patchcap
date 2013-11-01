patchcap
========

capturador de patentes basado en SimpleCV


1) Demonio PatchFinder


2)Herramienta de configuracion y consulta patchup

./patchup.py -h 

para ver las opciones disponibles:

./patchup.py
	[-b | --generate-db] <base.db>
	[-a | --add-plate] <XXXNNN>
	[-d | --delete-plate] <XXXNNN>
	[-l | --list-all] 


 
2.1) Crear y/o regenerar base de datos
cd patchcap/

./patchup -b patchcap.db

ATENCION: Si ya existe una base con el mismo nombre, se resetea y se elimina toda la informacion.

2.2) Dar de alta una patente

./patchup -a LYD134 

Se agrega la patente al registro de patentes conocidas. 
Si ya existia un registro con el mismo nro, se ignora el comando. 

2.3) 

./patchup -a LYD134 
Se elimina la patente de la base y todos sus registros asociados. 
Si no existe, se ignora el comando
