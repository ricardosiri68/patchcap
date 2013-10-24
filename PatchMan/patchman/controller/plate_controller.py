from patchman.models import Plate,Brand, PlateLog, DBSession
from formencode import validators
from formencode.schema import Schema
from pyramid.httpexceptions import HTTPFound
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

class PlateForm(Schema):
    """ plate form schema for validation
        TODO: DRY code, sqlalchemy model validation instead?
    """
    filter_extra_fields = True
    allow_extra_fields = True
    code = validators.String(not_empty=True)
    brand_id = validators.Int()
    active = validators.Bool()
    notes = validators.String()

@view_config(route_name="plate_list")
def list(request):
    """plates list """
    search = request.params.get("search", "")
        
    sort= "code"
    if request.GET.get("sort") and request.GET.get("sort") in \
            ["code", "brand"]:
        sort = request.GET.get("sort")
    if sort == "brand":
        sort = "brand.name"    
    
    direction = "asc"
    if request.GET.get("direction") and request.GET.get("direction") in ["asc", "desc"]:
        direction = request.GET.get("direction")

    # db query     
    dbsession = DBSession()
    query = dbsession.query(Plate).join(PlateLog).\
        filter(Plate.code.like(search + "%")).\
                   order_by(sort + " " + direction)
    
    # paginate
    page_url = paginate.PageURL_WebOb(request)
    plates = Page(query, 
                     page=int(request.params.get("page", 1)), 
                     items_per_page=10, 
                     url=page_url)
        
    if "partial" in request.params:
        # Render the partial list page
        return render_to_response("plate/listPartial.html",
                                  {"plates": plates},
                                  request=request)
    else:
        # Render the full list page
        return render_to_response("plate/list.html",
                                  {"plates": plates},
                                  request=request)


@view_config(route_name="plate_search")
def search(request):
    """plates list searching """
    sort = request.GET.get("sort") if request.GET.get("sort") else "code" 
    direction = "desc" if request.GET.get("direction") == "asc" else "asc" 
    query = {"sort": sort, "direction": direction}
    
    return HTTPFound(location = request.route_url("plate_list", _query=query))

@view_config(route_name="plate_new", renderer="plate/new.html", permission="add")
def new(request):
    """new plate """
    brands = get_brands()
    
    form = Form(request, schema=PlateForm)    
    if "form_submitted" in request.POST and form.validate():
        dbsession = DBSession()
        plate = form.bind(Plate())
        dbsession.add(plate)
        request.session.flash("warning;Nueva Patente guardada!")
        return HTTPFound(location = request.route_url("plate_list"))
        
    return dict(form=FormRenderer(form),
                brands=brands, 
                action_url=request.route_url("plate_new"))

@view_config(route_name="plate_edit", renderer="plate/edit.html", permission="edit")
def edit(request):
    """plate edit """
    id = request.matchdict['id']
    dbsession = DBSession()
    plate = dbsession.query(Plate).filter_by(id=id).one()
    if plate is None:
        request.session.flash("error;Patente no encontrada!")
        return HTTPFound(location=request.route_url("plate_list"))        
    
    brands = get_brands()
    
    form = Form(request, schema=PlateForm, obj=plate)    
    if "form_submitted" in request.POST and form.validate():
        form.bind(plate)
        dbsession.add(plate)
        request.session.flash("warning;Se guardo la patente!")
        return HTTPFound(location = request.route_url("plate_list"))

    action_url = request.route_url("plate_edit", id=id)
    return dict(form=FormRenderer(form),
                brands=brands, 
                action_url=action_url)

@view_config(route_name="plate_delete", permission="delete")
def delete(request):
    """plate delete """
    id = request.matchdict['id']
    dbsession = DBSession()
    plate = dbsession.query(plate).filter_by(id=id).first()
    if plate is None:
        request.session.flash("error;Patente no encontrada!")
        return HTTPFound(location=request.route_url("plate_list"))        
    
    try:
        transaction.begin()
        dbsession.delete(plate);
        transaction.commit()
        request.session.flash("warning;Se elimino la patente!")
    except IntegrityError:
        # delete error
        transaction.abort()
        request.session.flash("error;La patente no se pudo eliminar!")
    
    return HTTPFound(location=request.route_url("plate_list"))

def get_brands():
    """Gets all brands with id, name value pairs """
    dbsession = DBSession()
    brands_q = dbsession.query(Brand).order_by(Brand.name)
    brands = [(brand.id, brand.name) for brand in brands_q.all()]
    
    return brands
