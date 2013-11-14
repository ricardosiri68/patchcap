class MyRoutes:
	__security = 'patchman.security.EntryFactory'
	__routes = (
			# inicio y pltaforma
			("home","/"),
			("home_dashboard","/home/dashboard"),

			# marcas y modelos
			("brand_list","/brands/list"),
			("brand_search", "/brands/search"),
			("brand_new","/brands/new", __security),
			("brand_edit","/brands/{id}/edit",__security),
			("brand_delete","/brands/{id}/delete",__security),

			# camaras y dispositivos
			("device_discover","/devices/discover"),
			("device_list","/devices/list"),
			("device_search","/devices/search"),
			("device_new","/devices/new", __security),
			("device_view","/device/{id}/view",__security),
			("device_edit","/device/{id}/edit",__security),
			("device_delete","/device/{id}/delete",__security),

			# patentes registradas
			("plate_list", "/plates/list"),
			("plate_search", "/plates/search"),
			("plate_new", "/plates/new", __security),
			("plate_edit", "/plates/edit", __security),
			("plate_delete", "/plates/delete", __security),

			# registro de captura
			("log_get", "/logs/get"),

			# control de acceso
			("auth","/sign/{action}")
		)

	def __init__(self, config):
		self.__config = config
		self.addRoutes()

	def addRoutes(self):
		for r in self.__routes:
			if(len(r) == 2):
				self.__config.add_route(r[0],r[1])
			elif(len(r) == 3):
				self.__config.add_route(r[0],r[1], factory = r[2])
