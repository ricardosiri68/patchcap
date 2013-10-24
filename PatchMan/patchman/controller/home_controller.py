from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name="home")
def home(request):
    """home """
    return HTTPFound(location = request.route_url("home_dashboard"))

@view_config(route_name="home_dashboard", renderer="home/dashboard.html")
def dashboard(request):
    """dashboard """
    return {"dashboard": "Dashboard"}
