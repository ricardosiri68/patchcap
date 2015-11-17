
#Users
#list
curl -XGET -i localhost/api/users

#add
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Name Lastname","username":"user", "password":"pepe","email":"user@mirich.com.ar"}' localhost/api/users

#get id = 1
curl -XGET -i localhost/api/users/1

#update
curl -i -H "Content-Type: application/json" -X PUT -d '{"name":"Name Lastname","username":"other", "password":"pwd", "email":"other@mirich.com.ar"}' localhost/api/users/1

#update. set profile. ignore password if not set
curl -b auth-cookie.txt -i -H "Content-Type: application/json" -X PUT -d '{"profiles":[{"id":1}], "name":"H","username":"hernando", "email":"hernando@lacuatro.com.ar"}' localhost/api/users/1

#del
curl -X DELETE -i localhost/api/users/1


#login
curl -c auth-cookie.txt -i -H "Content-Type: application/json" -X POST -d '{"username":"user", "password":"pass"}' localhost/api/users/login

#authenticad list
curl -b auth-cookie.txt -XGET -i localhost/api/devices

#profiles
curl -b auth-cookie.txt -i -H "Content-Type: application/json" -X POST -d '{"name":"Supervisor"}' localhost/api/profiles


#Cams

#list
curl -XGET -i localhost/api/devices

#get id=1
curl -XGET -i localhost/api/devices/1

#add
curl -i -H "Content-Type: application/json" -X POST -d '{"instream":"rtsp://192.168.2.3:554/cam/realmonitor?channel=1&subtype=0&authbasic=YWRtaW46YWRtaW4=","ip":"192.168.2.3", "outstream":"poste2","name":"hola2"}' localhost/api/devices

#upd el id=5
curl -i -H "Content-Type: application/json" -X PUT -d '{"instream:"rtsp://192.168.2.3:554/cam/realmonitor?channel=1&subtype=0&authbasic=YWRtaW46YWRtaW4=","ip":"192.168.2.3", "outstream":"poste22","name":"hola2"}' localhost/api/devices/5

#del id=2
curl -X DELETE -i localhost/api/devices/2


#"logging"
curl -b auth-cookie.txt -i -H"Content-Type: application/json" -XPOST -d{"device_id":1, "ts":"2015-11-22T10:00", "roi":"0,200,200,100","code":"ppp222","conf":"80,60,70,90,90,90"} localhost/api/logs
