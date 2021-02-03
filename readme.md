# MELI Scraper + CUIT fuzzy matching

Implementación de un webscraper (`scrapy.py`) de articulos y vendedores en [Mercado Libre](https://www.mercadolibre.com.ar). La segunda parte (`process.py`) hace un streaming de la data crawleada e identifica CUITs usando la base de [Registro Nacional de Sociedades](https://www.argentina.gob.ar/justicia/registro-nacional-sociedades). Finalmente, identifica si el usuario en MELI es cliente.

## Uso

- `pip install -r requirements.txt`

Scraper:
- `python scraper.py` 

Matching (con base de Registro Nacional de Sociedades)
- `python match.py` 

Ambos procesos en concurrencia
- `python concurrence.py` 

***Output***

Scraper
```json
{"time": "2020-12-29 14:43:10", "seller_id": 188316739, "data": {"id": 188316739, "nickname": "ELECTRO LAND", "permalink": "http://perfil.mercadolibre.com.ar/ELECTRO+LAND", "registration_date": "2015-07-21T23:31:46.000-04:00", "seller_reputation": {"level_id": "5_green", "power_seller_status": "platinum", "transactions": {"total": 178618, "canceled": 10710, "period": "historic", "ratings": {"negative": 0.03, "positive": 0.95, "neutral": 0.02}, "completed": 167908}, "metrics": {"sales": {"period": "60 days", "completed": 41230}}}, "tags": ["normal", "user_info_verified", "credits_priority_4", "credits_profile", "eshop", "mshops", "medium_seller", "messages_as_seller", "messages_as_buyer"], "eshop": {"nick_name": "ELECTRO LAND", "eshop_rubro": null, "eshop_id": 349328, "eshop_locations": [], "site_id": "MLA", "eshop_logo_url": "http://resources.mlstatic.com/eshops/188316739v358f61.png", "eshop_status_id": 1, "seller": 188316739, "eshop_experience": 0}, "cantidad_articulos": 387, "cantidad_ventas": 346967, "revenue": 641512833}, "seller_address_2": {"id": "", "comment": "", "address_line": "", "zip_code": "", "country": {"id": "AR", "name": "Argentina"}, "state": {"id": "AR-C", "name": "Capital Federal"}, "city": {"id": "TUxBQkJPRTQ0OTRa", "name": "Boedo"}, "latitude": "", "longitude": ""}, "seller_address": {"city": {"id": "TUxBQkJPRTQ0OTRa", "name": "Boedo"}, "state": {"id": "AR-C", "name": "Capital Federal"}, "country": {"id": "AR", "name": "Argentina"}, "search_location": {"neighborhood": {"id": "TUxBQkJPRTQ0OTRa", "name": "Boedo"}, "city": {"id": "TUxBQ0NBUGZlZG1sYQ", "name": "Capital Federal"}, "state": {"id": "TUxBUENBUGw3M2E1", "name": "Capital Federal"}}, "id": 169366040}}
{"time": "2020-12-29 14:48:50", "seller_id": 544738861, "data": {"id": 544738861, "nickname": "RENTAL GNC", "permalink": "http://perfil.mercadolibre.com.ar/RENTAL+GNC", "registration_date": "2020-04-10T18:32:25.000-04:00", "seller_reputation": {"level_id": "5_green", "power_seller_status": "gold", "transactions": {"total": 716, "canceled": 35, "period": "historic", "ratings": {"negative": 0.05, "positive": 0.87, "neutral": 0.08}, "completed": 681}, "metrics": {"sales": {"period": "60 days", "completed": 275}}}, "tags": ["normal", "user_info_verified", "mshops", "credits_profile", "messages_as_seller", "messages_as_buyer"], "eshop": null, "cantidad_articulos": 17, "cantidad_ventas": 693, "revenue": 6128128.0}, "seller_address_2": {"id": "", "comment": "", "address_line": "", "zip_code": "", "country": {"id": "AR", "name": "Argentina"}, "state": {"id": "AR-B", "name": "Buenos Aires"}, "city": {"id": null, "name": "Villa Lynch"}, "latitude": "", "longitude": ""}, "seller_address": {"city": {"name": "Villa Lynch"}, "state": {"id": "AR-B", "name": "Buenos Aires"}, "country": {"id": "AR", "name": "Argentina"}, "search_location": {"neighborhood": {"id": "TUxBQlZJTDg5NDBa", "name": "Villa Lynch"}, "city": {"id": "TUxBQ0dFTmVyYWxz", "name": "General San Mart\u00edn"}, "state": {"id": "TUxBUEdSQWU4ZDkz", "name": "Bs.As. G.B.A. Norte"}}, "id": 1109716618}}

```
Matching


```json
{"seller_id": 188316739, "match": {"data_empresas": [{"cuit": 30680075820, "razon_social": "ELECTROLAND SRL", "fecha_contrato_social": "1994-10-11-00:00", "tipo_societario": "SOCIEDAD DE RESPONSABILIDAD LIMITADA", "fecha_actualizacion": null, "numero_inscripcion": -1, "dom_fiscal_provincia": "CAPITAL FEDERAL", "dom_fiscal_localidad": "CAPITAL FEDERAL", "dom_fiscal_calle": "MI\u00d1ONES", "dom_fiscal_numero": 1941, "dom_fiscal_piso": null, "dom_fiscal_departamento": null, "dom_fiscal_cp": 1428, "dom_fiscal_estado_domicilio": "NO NOTIFICADO", "dom_legal_provincia": "CIUDAD AUTONOMA BUENOS AIRES", "dom_legal_localidad": "CAPITAL FEDERAL", "dom_legal_calle": "MI#ONES", "dom_legal_numero": 1941, "dom_legal_piso": null, "dom_legal_departamento": null, "dom_legal_cp": 1428, "dom_legal_estado_domicilio": "NO CONFIRMADO"}], "party_id": null}, "matched": true}
{"seller_id": 544738861, "match": {"data_empresas": null, "party_id": null}, "matched": false}
```