#Users
#list
curl -XGET -i localhost:8080/api/users

#add
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Name Lastname","username":"user", "password":"pepe","email":"user@mirich.com.ar"}' localhost:8080/api/users

#get id = 1
curl -XGET -i localhost:8080/api/users/1

#update
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"Name Lastname","username":"user", "password":"pepe2","email":"other@mirich.com.ar"}' localhost:8080/api/users

#del
curl -X DELETE -i localhost:8080/api/users/1


#login
curl -c auth-cookie.txt -i -H "Content-Type: application/json" -X POST -d '{"username":"user", "password":"pass"}' localhost:8080/api/users/login
curl -c auth-cookie.txt -i -H "Content-Type: application/json" -X POST -d {username:hernando, password:nonsecurepass} localhost:8080/api/users/login

#authenticad list
curl -b auth-cookie.txt -XGET -i localhost:8080/api/devices


#Cams

#list
curl -XGET -i localhost:8080/api/devices

#get id=1
curl -XGET -i localhost:8080/api/devices/1

#add
curl -i -H "Content-Type: application/json" -X POST -d '{"instream":"rtsp://192.168.2.3:554/cam/realmonitor?channel=1&subtype=0&authbasic=YWRtaW46YWRtaW4=","ip":"192.168.2.3", "outstream":"poste2","name":"hola2"}' localhost:8080/api/devices

#upd el id=5
curl -i -H "Content-Type: application/json" -X PUT -d '{"instream:"rtsp://192.168.2.3:554/cam/realmonitor?channel=1&subtype=0&authbasic=YWRtaW46YWRtaW4=","ip":"192.168.2.3", "outstream":"poste22","name":"hola2"}' localhost:8080/api/devices/5

#del id=2
curl -X DELETE -i localhost:8080/api/devices/2



