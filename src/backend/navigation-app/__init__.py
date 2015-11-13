

def includeme(config):
    config.add_static_view(name='frontend', path='./')
    # Let other apps reuse our library aassets.
