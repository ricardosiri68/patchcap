from patchman.models import Brand, DBSession
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

class BrandForm(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    name = validators.String(not_empty=True)

@view_config(route_name="brand_list")
def list(request):
    """brands list """
    search = request.params.get("search", "")
        
    sort= "name"
    if request.GET.get("sort") and request.GET.get("sort") == "name":
        sort = request.GET.get("sort")
    
    direction = "asc"
    if request.GET.get("direction") and request.GET.get("direction") in ["asc", "desc"]:
        direction = request.GET.get("direction")
     
    # db query     
    dbsession = DBSession()
    query = dbsession.query(Brand).\
        filter(Brand.name.like(search + "%")).\
        order_by(sort + " " + direction)

    # paginate
    page_url = paginate.PageURL_WebOb(request)
    brands = Page(query, 
                     page=int(request.params.get("page", 1)), 
                     items_per_page=10, 
                     url=page_url)
    
    if "partial" in request.params:
        # Render the partial list page
        return render_to_response("brand/listPartial.html",
                                  {"brands": brands},
                                  request=request)
    else:
        # Render the full list page
        return render_to_response("brand/list.html",
                                  {"brands": brands},
                                  request=request)

@view_config(route_name="brand_search")
def search(request):
    """brands list searching """
    sort = request.GET.get("sort") if request.GET.get("sort") else "name" 
    direction = "desc" if request.GET.get("direction") == "asc" else "asc" 
    query = {"sort": sort, "direction": direction}
    
    return HTTPFound(location=request.route_url("brand_list", _query=query))

@view_config(route_name="brand_new", renderer="brand/new.html", permission="add")
def new(request):
    """new country """
    form = Form(request, schema=BrandForm)    
    if "form_submitted" in request.POST and form.validate():
        dbsession = DBSession()
        brand = form.bind(Brand())
        # TODO: db error control?
        dbsession.add(brand)
        request.session.flash("warning;Se guardo la marca!")
        return HTTPFound(location = request.route_url("brand_list"))
        
    return dict(form=FormRenderer(form), 
                action_url=request.route_url("brand_new"))

@view_config(route_name="brand_edit", renderer="brand/edit.html", permission="edit")
def edit(request):
    """brand edit """
    id = request.matchdict['id']
    dbsession = DBSession()
    brand = dbsession.query(Brand).filter_by(id=id).one()
    if brand is None:
        request.session.flash("error;No se encontro la marca!")
        return HTTPFound(location=request.route_url("brand_list"))        
    

    form = Form(request, schema=BrandForm, obj=brand)    
    if "form_submitted" in request.POST and form.validate():
        form.bind(brand)
        dbsession.add(brand)
        request.session.flash("warning;Se guardo la marca!")
        return HTTPFound(location = request.route_url("brand_list"))

    action_url = request.route_url("brand_edit", id=id)
    return dict(form=FormRenderer(form), 
                action_url=action_url)
    
@view_config(route_name="brand_delete", permission="delete")
def delete(request):
    """brand delete """
    id = request.matchdict['id']
    dbsession = DBSession()
    brand = dbsession.query(Brand).filter_by(id=id).first()
    if brand is None:
        request.session.flash("error;Marca inexistente!")
        return HTTPFound(location=request.route_url("brand_list"))        
    
    try:
        transaction.begin()
        dbsession.delete(brand);
        transaction.commit()
        request.session.flash("warning;Marca inexistente!")
    except IntegrityError:
        # delete error
        transaction.abort()
        request.session.flash("error;No se pudo eliminar la marca. Verifique que no este siendo usada por ningun registro!")
    
    return HTTPFound(location=request.route_url("brand_list"))
