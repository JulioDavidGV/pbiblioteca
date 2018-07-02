from flask.globals import _app_ctx_stack
from flask.globals import _request_ctx_stack
from werkzeug.urls import url_parse
from werkzeug.exceptions import NotFound


def split_url(url, method='GET'):
    """Devuelve el nombre del puntofinal y los argumentos que coinciden con una url determinada. En
    otras palabras, esta funcion es un reverso de url_for() de flask."""

    appctx = _app_ctx_stack.top
    reqctx = _request_ctx_stack.top

    if appctx is None:
        raise RuntimeError('Intentó hacer coincidir una URL sin que'
                'se empujara el contexto de la aplicación. Esto debe ejecutarse'
                'cuando el contexto de la aplicación esté disponible.')

    if reqctx is not None:
        url_adapter = reqctx.url_adapter
    else:
        url_adapter = appctx.url_adapter
        if url_adapter is None:
            raise RuntimeError('La aplicación no pudo crear un adaptador de URL para la '
                               'coincidencia de URL independiente de la solicitud.'
                               'Es posible que pueda solucionar esto configurando la '
                               'variable de configuración SERVER_NAME')

    parsed_url = url_parse(url)
    if parsed_url.netloc is not '' and parsed_url.netloc != url_adapter.server_name:
        raise ValidationError('URL Inválido:' + url)
    try:
        result = url_adapter.match(parsed_url.path, method)
    except NotFound:
        raise ValidationError('URL Inválido: ' + URL)
    return result

