from patchman.models import Device, DBSession
from formencode import validators
from formencode.schema import Schema
from pyramid.httpexceptions import (HTTPFound, HTTPNotFound)
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from sqlalchemy.exc import IntegrityError
from webhelpers import paginate
from webhelpers.paginate import Page
import logging
import transaction

log = logging.getLogger(__name__)

class DeviceForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    name = validators.String(not_empty=True)

@view_config(route_name="device_list")
def list(request):
    """devices list """
    search = request.params.get("search", "")
        
    sort= "name"
    if request.GET.get("sort") and request.GET.get("sort") == "name":
        sort = request.GET.get("sort")
    
    direction = "asc"
    if request.GET.get("direction") and request.GET.get("direction") in ["asc", "desc"]:
        direction = request.GET.get("direction")
     
    # db query     
    dbsession = DBSession()
    query = dbsession.query(Device).\
        filter(Device.name.like(search + "%")).\
        order_by(sort + " " + direction)

    # paginate
    page_url = paginate.PageURL_WebOb(request)
    devices = Page(query, 
                     page=int(request.params.get("page", 1)), 
                     items_per_page=10, 
                     url=page_url)
    
    if "partial" in request.params:
        # Render the partial list page
        return render_to_response("device/listPartial.html",
                                  {"devices": devices},
                                  request=request)
    else:
        # Render the full list page
        return render_to_response("device/list.html",
                                  {"devices": devices},
                                  request=request)

@view_config(route_name="device_search")
def search(request):
    """devices list searching """
    sort = request.GET.get("sort") if request.GET.get("sort") else "name" 
    direction = "desc" if request.GET.get("direction") == "asc" else "asc" 
    query = {"sort": sort, "direction": direction}
    
    return HTTPFound(location=request.route_url("device_list", _query=query))

@view_config(route_name="device_new", renderer="device/new.html", permission="add")
def new(request):
    """new country """
    form = Form(request, schema=DeviceForm)    
    if "form_submitted" in request.POST and form.validate():
        dbsession = DBSession()
        device = form.bind(Device())
        # TODO: db error control?
        dbsession.add(device)
        request.session.flash("warning;New Device is saved!")
        return HTTPFound(location = request.route_url("device_list"))
        
    return dict(form=FormRenderer(form), 
                action_url=request.route_url("device_new"))

@view_config(route_name="device_edit", renderer="device/edit.html", permission="edit")
def edit(request):
    """device edit """
    id = request.matchdict['id']
    dbsession = DBSession()
    device = dbsession.query(Device).filter_by(id=id).one()
    if device is None:
        request.session.flash("error;Device not found!")
        return HTTPFound(location=request.route_url("device_list"))        
    

    form = Form(request, schema=DeviceForm, obj=device)    
    if "form_submitted" in request.POST and form.validate():
        form.bind(device)
        dbsession.add(device)
        request.session.flash("warning;The Device is saved!")
        return HTTPFound(location = request.route_url("device_list"))

    action_url = request.route_url("device_edit", id=id)
    return dict(form=FormRenderer(form), 
                action_url=action_url)
   
@view_config(route_name='device_view', renderer="device/view.html")
def view(request):
    id = int(request.matchdict.get('id', -1))
    device = Device.by_id(id) if id>0 else  Device.first()
    if not device:
        return HTTPNotFound()
    return {'device':device}

 
@view_config(route_name="device_delete", permission="delete")
def delete(request):
    """device delete """
    id = request.matchdict['id']
    dbsession = DBSession()
    device = dbsession.query(Device).filter_by(id=id).first()
    if device is None:
        request.session.flash("error;Device not found!")
        return HTTPFound(location=request.route_url("device_list"))        
    
    try:
        transaction.begin()
        dbsession.delete(device);
        transaction.commit()
        request.session.flash("warning;The device is deleted!")
    except IntegrityError:
        # delete error
        transaction.abort()
        request.session.flash("error;The device could not be deleted!")
    
    return HTTPFound(location=request.route_url("device_list"))
