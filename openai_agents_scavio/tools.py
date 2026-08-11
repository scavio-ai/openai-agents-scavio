"""Scavio tools for the OpenAI Agents SDK.

Build the tools with `get_scavio_tools()` and pass them to an Agent:

    from agents import Agent
    from openai_agents_scavio import get_scavio_tools

    agent = Agent(name="Search", tools=get_scavio_tools())

Covers the whole Scavio API across 31 platforms - Google, YouTube, Amazon,
Walmart, Reddit, TikTok, TikTok Shop, Instagram, X, LinkedIn, Threads, Kuaishou,
eBay, Target, Home Depot, Zillow, Redfin, Booking.com, Airbnb, Tripadvisor, Yelp,
Indeed, Glassdoor, App Store, Google Play, SEC EDGAR, Companies House, G2,
Capterra, Google Ads Transparency and the Meta Ad Library - plus the top-level
`extract` endpoint that reads any URL as HTML, Markdown or plain text.

188 tools over the 195 endpoints the Scavio SDK exposes. The seven that are not
registered are dead or duplicate surfaces: /youtube/metadata (a deprecated alias
of /youtube/video), /amazon/options (a keyless static marketplace list, not a
search), and the five LinkedIn endpoints the upstream provider withdrew, which
always return HTTP 410.

Each platform is gated by an ``enable_*`` flag. Tools return the Scavio JSON response.
"""

import os
from typing import Any, Callable, Dict, Literal, Optional

from agents import function_tool

try:
    from scavio import ScavioClient
except ImportError as exc:  # pragma: no cover
    raise ImportError("`scavio` not installed. Please install using `pip install scavio`") from exc


def _run(call: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    """Run a Scavio SDK call, returning its JSON dict or an {"error": ...} dict."""
    try:
        return call()
    except Exception as exc:  # noqa: BLE001 - surface errors to the agent
        return {"error": str(exc)}


def get_scavio_tools(
    api_key: Optional[str] = None,
    *,
    enable_google: bool = True,
    enable_amazon: bool = True,
    enable_walmart: bool = True,
    enable_youtube: bool = True,
    enable_reddit: bool = True,
    enable_tiktok: bool = True,
    enable_tiktok_shop: bool = True,
    enable_instagram: bool = True,
    enable_x: bool = True,
    enable_linkedin: bool = True,
    enable_threads: bool = True,
    enable_kuaishou: bool = True,
    enable_ebay: bool = True,
    enable_target: bool = True,
    enable_home_depot: bool = True,
    enable_zillow: bool = True,
    enable_booking: bool = True,
    enable_tripadvisor: bool = True,
    enable_indeed: bool = True,
    enable_airbnb: bool = True,
    enable_glassdoor: bool = True,
    enable_yelp: bool = True,
    enable_app_store: bool = True,
    enable_google_play: bool = True,
    enable_sec: bool = True,
    enable_redfin: bool = True,
    enable_companies_house: bool = True,
    enable_g2: bool = True,
    enable_capterra: bool = True,
    enable_google_ads: bool = True,
    enable_meta_ads: bool = True,
    enable_extract: bool = True,
    all: bool = False,
) -> list:
    """Build Scavio function tools for an OpenAI Agents SDK Agent.

    Args:
        api_key: Scavio API key. Falls back to the SCAVIO_API_KEY env var.
        enable_google: Register the Google tools (14). Defaults to True.
        enable_amazon: Register the Amazon tools (3). Defaults to True.
        enable_walmart: Register the Walmart tools (7). Defaults to True.
        enable_youtube: Register the YouTube tools (15). Defaults to True.
        enable_reddit: Register the Reddit tools (12). Defaults to True.
        enable_tiktok: Register the TikTok tools (11). Defaults to True.
        enable_tiktok_shop: Register the TikTok Shop tools (8). Defaults to True.
        enable_instagram: Register the Instagram tools (12). Defaults to True.
        enable_x: Register the X tools (11). Defaults to True.
        enable_linkedin: Register the LinkedIn tools (9). Defaults to True.
        enable_threads: Register the Threads tools (6). Defaults to True.
        enable_kuaishou: Register the Kuaishou tools (14). Defaults to True.
        enable_ebay: Register the eBay tools (3). Defaults to True.
        enable_target: Register the Target tools (4). Defaults to True.
        enable_home_depot: Register the Home Depot tools (3). Defaults to True.
        enable_zillow: Register the Zillow tools (3). Defaults to True.
        enable_booking: Register the Booking.com tools (3). Defaults to True.
        enable_tripadvisor: Register the Tripadvisor tools (4). Defaults to True.
        enable_indeed: Register the Indeed tools (4). Defaults to True.
        enable_airbnb: Register the Airbnb tools (3). Defaults to True.
        enable_glassdoor: Register the Glassdoor tools (4). Defaults to True.
        enable_yelp: Register the Yelp tools (3). Defaults to True.
        enable_app_store: Register the App Store tools (3). Defaults to True.
        enable_google_play: Register the Google Play tools (3). Defaults to True.
        enable_sec: Register the SEC EDGAR tools (6). Defaults to True.
        enable_redfin: Register the Redfin tools (3). Defaults to True.
        enable_companies_house: Register the Companies House tools (4). Defaults to True.
        enable_g2: Register the G2 tools (3). Defaults to True.
        enable_capterra: Register the Capterra tools (3). Defaults to True.
        enable_google_ads: Register the Google Ads Transparency tools (3). Defaults to True.
        enable_meta_ads: Register the Meta Ad Library tools (3). Defaults to True.
        enable_extract: Register the top-level extract tool (1). Defaults to True.
        all: Register every tool, ignoring the individual flags.
    """
    client = ScavioClient(api_key=api_key or os.getenv("SCAVIO_API_KEY"))
    tools: list = []

    # Google is v2 only: /api/v1/google was sunset on 2026-08-04 and now returns
    # 410. The v1 param spellings (light_request, country_code, language,
    # search_type, page) went with it; v2 takes gl, hl, start, google_domain and
    # device, and every Google tool below uses those names verbatim.
    if all or enable_google:
        @function_tool
        def scavio_google_search(query: str, device: Optional[Literal["desktop", "mobile"]] = None, start: Optional[int] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None, lr: Optional[str] = None, cr: Optional[str] = None, safe: Optional[Literal["active"]] = None, nfpr: Optional[bool] = None, filter: Optional[Literal["0", "1"]] = None, time_period: Optional[Literal["last_hour", "last_day", "last_week", "last_month", "last_year"]] = None, resolve_ai_overview: Optional[bool] = None, include_html: Optional[bool] = None) -> dict:
            """Search Google for real-time web results: organic_results (title, link, snippet), ads, and the AI Overview when present. Costs 1 credit.

            Args:
                query: The search query (1-500 characters).
                device: Device to emulate: desktop or mobile.
                start: Result offset: 0 = page 1, 10 = page 2, up to 990.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                google_domain: Regional Google domain, e.g. google.co.uk.
                location: Canonical location name; auto-encoded to a UULE string.
                uule: Pre-encoded UULE location string (takes priority over location).
                lr: Language restrict, e.g. lang_en.
                cr: Country restrict, e.g. countryUS.
                safe: SafeSearch filter; 'active' is the only value.
                nfpr: Disable spelling correction / auto-fixes when true.
                filter: '0' disables the omitted/similar-results filter, '1' keeps it.
                time_period: Recent time window: last_hour, last_day, last_week, last_month, last_year.
                resolve_ai_overview: Resolve a deferred AI Overview (server default true).
                include_html: Include the raw Google HTML in the response. Large; leave off unless parsing it.
            """
            _p = {"query": query, "device": device, "start": start, "hl": hl, "gl": gl, "google_domain": google_domain, "location": location, "uule": uule, "lr": lr, "cr": cr, "safe": safe, "nfpr": nfpr, "filter": filter, "time_period": time_period, "resolve_ai_overview": resolve_ai_overview, "include_html": include_html}
            return _run(lambda: client.google.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_search)
        @function_tool
        def scavio_google_ai_mode(query: str, device: Optional[Literal["desktop", "mobile"]] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None, safe: Optional[Literal["active"]] = None, include_html: Optional[bool] = None) -> dict:
            """Get a Google AI Mode conversational answer with its source references, instead of a plain list of links. Costs 1 credit.

            Args:
                query: Question or prompt (1-500 characters).
                device: Device to emulate: desktop or mobile.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                google_domain: Regional Google domain, e.g. google.co.uk.
                location: Canonical location name; auto-encoded to a UULE string.
                uule: Pre-encoded UULE location string (takes priority over location).
                safe: SafeSearch filter; 'active' is the only value.
                include_html: Include the raw Google HTML in the response.
            """
            _p = {"query": query, "device": device, "hl": hl, "gl": gl, "google_domain": google_domain, "location": location, "uule": uule, "safe": safe, "include_html": include_html}
            return _run(lambda: client.google.ai_mode(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_ai_mode)
        @function_tool
        def scavio_google_maps_search(query: str, start: Optional[int] = None, ll: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None) -> dict:
            """Search Google Maps for local businesses. Each result carries name, address, rating, review count, place_id, data_cid and coordinates. Costs 1 credit.

            Args:
                query: The search query (1-500 characters).
                start: Result offset; must be a multiple of 20 (0, 20, 40, ...).
                ll: Map center as '@lat,lng,zoomz'; controls where results come from.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                google_domain: Regional Google domain, e.g. google.co.uk.
            """
            _p = {"query": query, "start": start, "ll": ll, "hl": hl, "gl": gl, "google_domain": google_domain}
            return _run(lambda: client.google.maps_search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_maps_search)
        @function_tool
        def scavio_google_maps_place(place_id: Optional[str] = None, data_cid: Optional[str] = None) -> dict:
            """Fetch Google Maps details for one place. Costs 1 credit.

            Args:
                place_id: Place ID (ChIJ...). Provide this or data_cid.
                data_cid: Numeric CID. Provide this or place_id.
            """
            _p = {"place_id": place_id, "data_cid": data_cid}
            return _run(lambda: client.google.maps_place(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_maps_place)
        @function_tool
        def scavio_google_maps_reviews(data_id: Optional[str] = None, place_id: Optional[str] = None, num: Optional[int] = None, next_page_token: Optional[str] = None, sort_by: Optional[Literal["relevance", "newest", "highest_rating", "lowest_rating"]] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None) -> dict:
            """List Google Maps reviews for a place. Costs 1 credit per page.

            Args:
                data_id: Data ID (0xHEX:0xHEX). Provide this or place_id.
                place_id: Place ID (ChIJ...). Provide this or data_id.
                num: Reviews per page (1-20).
                next_page_token: Pagination cursor from a prior response.
                sort_by: Sort order: relevance, newest, highest_rating, lowest_rating.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                google_domain: Regional Google domain, e.g. google.co.uk.
            """
            _p = {"data_id": data_id, "place_id": place_id, "num": num, "next_page_token": next_page_token, "sort_by": sort_by, "hl": hl, "gl": gl, "google_domain": google_domain}
            return _run(lambda: client.google.maps_reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_maps_reviews)
        @function_tool
        def scavio_google_shopping(query: str, device: Optional[Literal["desktop", "mobile"]] = None, start: Optional[int] = None, min_price: Optional[int] = None, max_price: Optional[int] = None, sort_by: Optional[int] = None, free_shipping: Optional[bool] = None, on_sale: Optional[bool] = None, shoprs: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None) -> dict:
            """Search Google Shopping product listings across merchants. Costs 1 credit.

            Args:
                query: Product search query (1-500 characters).
                device: Device to emulate: desktop or mobile.
                start: Result offset.
                min_price: Minimum price filter.
                max_price: Maximum price filter.
                sort_by: 0 = relevance, 1 = price ascending, 2 = price descending.
                free_shipping: Only items with free shipping.
                on_sale: Only items on sale.
                shoprs: Opaque Google Shopping filter token.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                google_domain: Regional Google domain, e.g. google.co.uk.
                location: Canonical location name; auto-encoded to a UULE string.
                uule: Pre-encoded UULE location string (takes priority over location).
            """
            _p = {"query": query, "device": device, "start": start, "min_price": min_price, "max_price": max_price, "sort_by": sort_by, "free_shipping": free_shipping, "on_sale": on_sale, "shoprs": shoprs, "hl": hl, "gl": gl, "google_domain": google_domain, "location": location, "uule": uule}
            return _run(lambda: client.google.shopping(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_shopping)
        @function_tool
        def scavio_google_shopping_product(catalog_id: Optional[str] = None, query: Optional[str] = None, immersive_product_page_token: Optional[str] = None, page_token: Optional[str] = None, product_id: Optional[str] = None, device: Optional[Literal["desktop", "mobile", "tablet"]] = None, sort_by: Optional[Literal["base_price", "total_price", "promotion", "seller_rating"]] = None, load_all_stores: Optional[bool] = None, more_stores: Optional[bool] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None) -> dict:
            """Fetch a Google Shopping product's detail page and its sellers. Pass catalog_id together with query for full data. Costs 1 credit.

            Args:
                catalog_id: Durable product catalog id.
                query: Product query; required when catalog_id is set.
                immersive_product_page_token: Immersive product page token.
                page_token: Alias for immersive_product_page_token.
                product_id: Product id.
                device: Device to emulate: desktop, mobile or tablet.
                sort_by: Seller sort order: base_price, total_price, promotion, seller_rating.
                load_all_stores: Load all available stores.
                more_stores: Fetch additional stores.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                google_domain: Regional Google domain, e.g. google.co.uk.
                location: Canonical location name; auto-encoded to a UULE string.
                uule: Pre-encoded UULE location string (takes priority over location).
            """
            _p = {"catalog_id": catalog_id, "query": query, "immersive_product_page_token": immersive_product_page_token, "page_token": page_token, "product_id": product_id, "device": device, "sort_by": sort_by, "load_all_stores": load_all_stores, "more_stores": more_stores, "hl": hl, "gl": gl, "google_domain": google_domain, "location": location, "uule": uule}
            return _run(lambda: client.google.shopping_product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_shopping_product)
        @function_tool
        def scavio_google_shopping_stores(catalog_id: str, next_page_token: str) -> dict:
            """Fetch more sellers for a Google Shopping product: the pagination leg of scavio_google_shopping_product. Costs 1 credit.

            Args:
                catalog_id: Durable product catalog id.
                next_page_token: Pagination cursor returned by scavio_google_shopping_product.
            """
            _p = {"catalog_id": catalog_id, "next_page_token": next_page_token}
            return _run(lambda: client.google.shopping_stores(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_shopping_stores)
        @function_tool
        def scavio_google_flights(departure_id: str, arrival_id: str, outbound_date: str, type: Optional[int] = None, return_date: Optional[str] = None, adults: Optional[int] = None, children: Optional[int] = None, infants_in_seat: Optional[int] = None, infants_on_lap: Optional[int] = None, travel_class: Optional[int] = None, stops: Optional[int] = None, sort_by: Optional[int] = None, include_airlines: Optional[str] = None, exclude_airlines: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None, currency: Optional[str] = None) -> dict:
            """Search Google Flights for itineraries and prices. Costs 1 credit.

            Args:
                departure_id: Departure IATA code(s); comma-separated allowed.
                arrival_id: Arrival IATA code(s); comma-separated allowed.
                outbound_date: Outbound date (YYYY-MM-DD).
                type: 1 = round trip, 2 = one way, 3 = multi-city.
                return_date: Return date (YYYY-MM-DD); required when type is 1.
                adults: Number of adults (1-9).
                children: Number of children (0-9).
                infants_in_seat: Infants in seat (0-4).
                infants_on_lap: Infants on lap (0-4).
                travel_class: 1 = economy, 2 = premium, 3 = business, 4 = first.
                stops: 0 = any, 1 = nonstop, 2 = one stop or fewer, 3 = two stops or fewer.
                sort_by: 1 = top, 2 = price, 3 = departure, 4 = arrival, 5 = duration, 6 = emissions.
                include_airlines: Comma-separated airline codes/alliances to include.
                exclude_airlines: Comma-separated airline codes/alliances to exclude.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                currency: Currency code (ISO 4217), e.g. USD.
            """
            _p = {"departure_id": departure_id, "arrival_id": arrival_id, "outbound_date": outbound_date, "type": type, "return_date": return_date, "adults": adults, "children": children, "infants_in_seat": infants_in_seat, "infants_on_lap": infants_on_lap, "travel_class": travel_class, "stops": stops, "sort_by": sort_by, "include_airlines": include_airlines, "exclude_airlines": exclude_airlines, "hl": hl, "gl": gl, "currency": currency}
            return _run(lambda: client.google.flights(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_flights)
        @function_tool
        def scavio_google_hotels(query: str, check_in_date: str, check_out_date: str, hl: Optional[str] = None, gl: Optional[str] = None, currency: Optional[str] = None, sort_by: Optional[int] = None, min_price: Optional[int] = None, max_price: Optional[int] = None, rating: Optional[int] = None, hotel_class: Optional[str] = None, amenities: Optional[str] = None, property_types: Optional[str] = None, free_cancellation: Optional[bool] = None, eco_certified: Optional[bool] = None, special_offers: Optional[bool] = None, next_page_token: Optional[str] = None, limit: Optional[int] = None) -> dict:
            """Search Google Hotels for properties, nightly rates and availability. Costs 1 credit.

            Args:
                query: Search query; use a '<City> hotels' form.
                check_in_date: Check-in date (YYYY-MM-DD).
                check_out_date: Check-out date (YYYY-MM-DD).
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                currency: Currency code (ISO 4217), e.g. USD.
                sort_by: 3 = lowest price, 8 = highest rating, 13 = most reviewed.
                min_price: Minimum nightly price.
                max_price: Maximum nightly price.
                rating: 7 = 3.5+, 8 = 4.0+, 9 = 4.5+.
                hotel_class: Comma-separated star ratings (2-5).
                amenities: Comma-separated amenity ids.
                property_types: Comma-separated property-type ids, e.g. '12' for vacation rentals.
                free_cancellation: Only properties with free cancellation.
                eco_certified: Only eco-certified properties.
                special_offers: Only properties with special offers.
                next_page_token: Pagination cursor from a prior response.
                limit: Number of properties to return (1-20).
            """
            _p = {"query": query, "check_in_date": check_in_date, "check_out_date": check_out_date, "hl": hl, "gl": gl, "currency": currency, "sort_by": sort_by, "min_price": min_price, "max_price": max_price, "rating": rating, "hotel_class": hotel_class, "amenities": amenities, "property_types": property_types, "free_cancellation": free_cancellation, "eco_certified": eco_certified, "special_offers": special_offers, "next_page_token": next_page_token, "limit": limit}
            return _run(lambda: client.google.hotels(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_hotels)
        @function_tool
        def scavio_google_hotels_detail(detail_token: str, check_in_date: str, check_out_date: str, currency: Optional[str] = None, gl: Optional[str] = None, hl: Optional[str] = None) -> dict:
            """Fetch full details for one Google Hotels property, using a detail_token from a hotels listing. Costs 1 credit.

            Args:
                detail_token: Property detail token from a scavio_google_hotels result.
                check_in_date: Check-in date (YYYY-MM-DD).
                check_out_date: Check-out date (YYYY-MM-DD).
                currency: Currency code (ISO 4217), e.g. USD.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                hl: UI language (ISO 639-1), e.g. en.
            """
            _p = {"detail_token": detail_token, "check_in_date": check_in_date, "check_out_date": check_out_date, "currency": currency, "gl": gl, "hl": hl}
            return _run(lambda: client.google.hotels_detail(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_hotels_detail)
        @function_tool
        def scavio_google_news(query: Optional[str] = None, topic_token: Optional[str] = None, section_token: Optional[str] = None, story_token: Optional[str] = None, publication_token: Optional[str] = None, kgmid: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, so: Optional[int] = None) -> dict:
            """Fetch Google News results. Provide a query, or a topic/story/publication token from a prior response. Costs 1 credit.

            Args:
                query: Keyword search.
                topic_token: Browse a news topic.
                section_token: Browse a topic section.
                story_token: Fetch full coverage of a story.
                publication_token: Browse a publication.
                kgmid: Knowledge Graph entity id.
                hl: UI language (ISO 639-1), e.g. en.
                gl: Country of the search (ISO 3166-1 alpha-2), e.g. us.
                google_domain: Regional Google domain, e.g. google.co.uk.
                so: Sort order: 0 = relevance, 1 = date. Only honoured with query or kgmid.
            """
            _p = {"query": query, "topic_token": topic_token, "section_token": section_token, "story_token": story_token, "publication_token": publication_token, "kgmid": kgmid, "hl": hl, "gl": gl, "google_domain": google_domain, "so": so}
            return _run(lambda: client.google.news(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_news)
        @function_tool
        def scavio_google_trends(query: str, geo: Optional[str] = None, hl: Optional[str] = None, date: Optional[str] = None, tz: Optional[str] = None, data_type: Optional[Literal["TIMESERIES", "GEO_MAP", "GEO_MAP_0", "RELATED_QUERIES", "RELATED_TOPICS"]] = None, cat: Optional[str] = None, gprop: Optional[Literal["images", "news", "youtube", "froogle"]] = None, region: Optional[Literal["COUNTRY", "REGION", "DMA", "CITY"]] = None) -> dict:
            """Fetch Google Trends interest data for one or more terms. Costs 1 credit.

            Args:
                query: Search term(s); comma-separated to compare up to five.
                geo: Location code, e.g. US, GB, US-CA.
                hl: UI language (ISO 639-1), e.g. en.
                date: Time range, e.g. 'today 12-m', 'now 7-d'.
                tz: Timezone offset in minutes.
                data_type: Dataset: TIMESERIES, GEO_MAP, GEO_MAP_0, RELATED_QUERIES, RELATED_TOPICS.
                cat: Category id.
                gprop: Google property filter: images, news, youtube, froogle.
                region: Resolution for GEO_MAP data: COUNTRY, REGION, DMA, CITY.
            """
            _p = {"query": query, "geo": geo, "hl": hl, "date": date, "tz": tz, "data_type": data_type, "cat": cat, "gprop": gprop, "region": region}
            return _run(lambda: client.google.trends(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_trends)
        @function_tool
        def scavio_google_trending(geo: str, hl: Optional[str] = None, hours: Optional[int] = None, cat: Optional[int] = None, sort: Optional[Literal["relevance", "search_volume", "recency", "title"]] = None, status: Optional[Literal["all", "active"]] = None) -> dict:
            """List Google Trending Now searches for a country. Costs 1 credit.

            Args:
                geo: Country code, e.g. US.
                hl: UI language (ISO 639-1), e.g. en.
                hours: Trending window: 4, 24, 48 or 168.
                cat: Category id (0-20).
                sort: Sort order: relevance, search_volume, recency, title.
                status: Filter by trend status: all or active.
            """
            _p = {"geo": geo, "hl": hl, "hours": hours, "cat": cat, "sort": sort, "status": status}
            return _run(lambda: client.google.trending(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_trending)

    if all or enable_amazon:
        # Amazon moved upstream in 2026-07: sort_by, pages, category_id,
        # merchant_id, language, currency, device, zip_code and
        # autoselect_variant no longer exist. Removed rather than kept as
        # no-ops - sort_by was verified to return the identical unordered set
        # for every value, and a dead param in a tool signature is a filter the
        # model plans against and never gets. domain still works on the wire as
        # a deprecated alias but is not offered: one spelling per param.
        @function_tool
        def scavio_amazon_search(query: str, country: Optional[str] = None, page: Optional[int] = None) -> dict:
            """Search Amazon for products matching a query. Results are unsorted and cannot be filtered. Costs 1 credit.

            Args:
                query: The product search query.
                country: Marketplace country code (ISO 3166-1 alpha-2), not a domain: us (default), gb (the UK is gb, not uk), ca, de, fr, es, it, jp, in, au, br, mx, nl, pl, se, sg, ae, sa, eg, cn, be, tr. An unknown code falls back to us.
                page: Result page, 1-based. One page per call, 1 credit each.
            """
            _p = {"query": query, "country": country, "page": page}
            return _run(lambda: client.amazon.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_amazon_search)
        @function_tool
        def scavio_amazon_product(asin: str, country: Optional[str] = None) -> dict:
            """Fetch full Amazon product details by ASIN. price is the buy-box price only. Costs 1 credit.

            Args:
                asin: Amazon Standard Identification Number (ASIN).
                country: Marketplace country code (ISO 3166-1 alpha-2), not a domain: us (default), gb (the UK is gb, not uk), ca, de, fr, es, it, jp, in, au, br, mx, nl, pl, se, sg, ae, sa, eg, cn, be, tr. An unknown code falls back to us.
            """
            _p = {"asin": asin, "country": country}
            return _run(lambda: client.amazon.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_amazon_product)
        @function_tool
        def scavio_amazon_offers(asin: str, country: Optional[str] = None) -> dict:
            """List every seller offer for an Amazon ASIN: price, seller, condition, shipping, buy box. Page 1 only. Costs 1 credit.

            Args:
                asin: Amazon Standard Identification Number (ASIN).
                country: Marketplace country code (ISO 3166-1 alpha-2), not a domain: us (default), gb (the UK is gb, not uk), ca, de, fr, es, it, jp, in, au, br, mx, nl, pl, se, sg, ae, sa, eg, cn, be, tr. An unknown code falls back to us.
            """
            _p = {"asin": asin, "country": country}
            return _run(lambda: client.amazon.offers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_amazon_offers)

    # Walmart is BODY-PRICED: `domain` sets the cost, com and ca at 1 credit and
    # com.mx at 2, and only search and category accept it (walmart.ca product
    # pages cannot be fetched at all). device, delivery_zip and store_id were
    # retired - sending them is not an error, the response just carries a
    # warnings[] array saying they were ignored. offers returns the BUY-BOX
    # seller only, and seller_products is the ~40 server-rendered items with no
    # page param at all.
    if all or enable_walmart:
        @function_tool
        def scavio_walmart_search(query: str, domain: Optional[Literal["com", "ca", "com.mx"]] = None, page: Optional[int] = None, sort_by: Optional[Literal["best_match", "price_low", "price_high", "best_seller", "rating_high", "new"]] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, fulfillment_speed: Optional[Literal["today", "tomorrow"]] = None, fulfillment_type: Optional[Literal["in_store"]] = None) -> dict:
            """Search Walmart and get structured product rows (products, products_count and the store the results were priced against). Costs 1 credit on domain 'com' or 'ca' and 2 credits on 'com.mx'.

            Args:
                query: Product search query (1-500 characters).
                domain: Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit), 'com.mx' (2 credits). Sets the currency and product URLs of the response.
                page: Results page, 1-based (integer >= 1). One page per call.
                sort_by: Result sort order. Defaults to 'best_match'. One of: best_match, price_low, price_high, best_seller, rating_high, new.
                min_price: Minimum price filter in the marketplace's own currency; decimals allowed (e.g. 19.99).
                max_price: Maximum price filter in the marketplace's own currency; decimals allowed (e.g. 199.5).
                fulfillment_speed: Only items deliverable today, or by tomorrow. '2_days' and 'anytime' are not accepted - for anytime, omit this parameter.
                fulfillment_type: Set to 'in_store' to return only items available for in-store pickup.
            """
            _p = {"query": query, "domain": domain, "page": page, "sort_by": sort_by, "min_price": min_price, "max_price": max_price, "fulfillment_speed": fulfillment_speed, "fulfillment_type": fulfillment_type}
            return _run(lambda: client.walmart.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_search)
        @function_tool
        def scavio_walmart_product(product_id: str) -> dict:
            """Full detail for a single Walmart product: price, rating, images, specifications, availability and seller. US marketplace only - walmart.ca product pages could not be fetched at all, so this endpoint takes no domain. Costs 1 credit. Walmart is body-priced through `domain`, but this endpoint takes no domain, so it is always 1.

            Args:
                product_id: Walmart item id (usItemId), e.g. '13544111159'.
            """
            _p = {"product_id": product_id}
            return _run(lambda: client.walmart.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_product)
        @function_tool
        def scavio_walmart_reviews(product_id: str, page: Optional[int] = None, sort: Optional[Literal["relevancy", "submission-desc", "submission-asc", "rating-desc", "rating-asc", "helpful-desc"]] = None) -> dict:
            """Customer reviews for a Walmart product with ratings, text, author, date and the rating breakdown. 10 reviews per page; paginate with page. Costs 1 credit. Walmart is body-priced through `domain`, but this endpoint takes no domain, so it is always 1.

            Args:
                product_id: Walmart item id (usItemId), e.g. '13544111159'.
                page: Reviews page, 1-based (integer >= 1). 10 reviews per page.
                sort: Review sort order. Omit for Walmart's own default ordering. One of: relevancy, submission-desc, submission-asc, rating-desc, rating-asc, helpful-desc.
            """
            _p = {"product_id": product_id, "page": page, "sort": sort}
            return _run(lambda: client.walmart.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_reviews)
        @function_tool
        def scavio_walmart_category(category_id: str, domain: Optional[Literal["com", "ca", "com.mx"]] = None, page: Optional[int] = None, limit: Optional[int] = None, sort_by: Optional[Literal["best_match", "price_low", "price_high", "best_seller", "rating_high", "new"]] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, fulfillment_speed: Optional[Literal["today", "tomorrow"]] = None) -> dict:
            """Products within a Walmart category, in the same product shape as search. Costs 1 credit on domain 'com' or 'ca' and 2 credits on 'com.mx'; `limit` trims the response after fetching and never reduces the cost.

            Args:
                category_id: Walmart category id: either a leaf id ('1095191') or the full underscore-joined path ('3944_133251_1095191'). Both are accepted.
                domain: Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit), 'com.mx' (2 credits). Sets the currency and product URLs of the response.
                page: Results page, 1-based (integer >= 1). One page per call.
                limit: Trim the returned products to at most this many (integer >= 1). Applied after fetching, so it does not reduce the credit cost of the call.
                sort_by: Result sort order. Defaults to 'best_match'. One of: best_match, price_low, price_high, best_seller, rating_high, new.
                min_price: Minimum price filter in the marketplace's own currency; decimals allowed (e.g. 19.99).
                max_price: Maximum price filter in the marketplace's own currency; decimals allowed (e.g. 199.5).
                fulfillment_speed: Only items deliverable today, or by tomorrow. '2_days' and 'anytime' are not accepted - for anytime, omit this parameter.
            """
            _p = {"category_id": category_id, "domain": domain, "page": page, "limit": limit, "sort_by": sort_by, "min_price": min_price, "max_price": max_price, "fulfillment_speed": fulfillment_speed}
            return _run(lambda: client.walmart.category(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_category)
        @function_tool
        def scavio_walmart_offers(product_id: str) -> dict:
            """The buy-box offer for a Walmart product: price, seller, condition and buy-box flag. BUY-BOX SELLER ONLY - this is not the full offer list, and there is no way to page through the other sellers. Costs 1 credit. Walmart is body-priced through `domain`, but this endpoint takes no domain, so it is always 1.

            Args:
                product_id: Walmart item id (usItemId), e.g. '2979510112'.
            """
            _p = {"product_id": product_id}
            return _run(lambda: client.walmart.offers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_offers)
        @function_tool
        def scavio_walmart_seller(seller_id: str) -> dict:
            """Marketplace seller storefront: name, rating, review count, Pro Seller badge and business details. Costs 1 credit. Walmart is body-priced through `domain`, but this endpoint takes no domain, so it is always 1.

            Args:
                seller_id: Numeric Walmart catalog seller id, as returned in `seller_catalog_id` on a product, search or offers response (e.g. '101480084'). The GUID `seller_id` is not accepted here - it 404s.
            """
            _p = {"seller_id": seller_id}
            return _run(lambda: client.walmart.seller(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_seller)
        @function_tool
        def scavio_walmart_seller_products(seller_id: str) -> dict:
            """A marketplace seller's catalog. Roughly the first 40 items are server-rendered and returned; total_count reports the seller's real catalog size. There is no pagination - the rest of the catalog is not reachable. Costs 1 credit. Walmart is body-priced through `domain`, but this endpoint takes no domain, so it is always 1.

            Args:
                seller_id: Numeric Walmart catalog seller id, as returned in `seller_catalog_id` on a product, search or offers response (e.g. '101480084'). The GUID `seller_id` 404s.
            """
            _p = {"seller_id": seller_id}
            return _run(lambda: client.walmart.seller_products(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_seller_products)

    if all or enable_youtube:
        @function_tool
        def scavio_youtube_search(query: str, upload_date: Optional[Literal["last_hour", "today", "this_week", "this_month", "this_year"]] = None, type: Optional[Literal["video", "channel", "playlist", "movie"]] = None, duration: Optional[Literal["short", "medium", "long"]] = None, sort_by: Optional[Literal["relevance", "date", "view_count", "rating"]] = None, features: Optional[list] = None, cursor: Optional[str] = None, hd: Optional[bool] = None, subtitles: Optional[bool] = None, creative_commons: Optional[bool] = None, live: Optional[bool] = None) -> dict:
            """Search YouTube for videos, channels, or playlists. Costs 2 credits.

            Args:
                query: The video search query.
                upload_date: Upload date filter: last_hour, today, this_week, this_month, this_year.
                type: Result type: video, channel, playlist, movie.
                duration: Duration filter: short, medium, long.
                sort_by: Sort order: relevance, date, view_count, rating.
                features: Feature filters, e.g. ['hd', '4k', 'subtitles', 'creative_commons', 'live', '360', '3d', 'hdr', 'vr180'].
                cursor: Pagination cursor from a prior response.
                hd: Restrict to HD videos when true.
                subtitles: Restrict to videos with subtitles when true.
                creative_commons: Restrict to Creative Commons videos when true.
                live: Restrict to live videos when true.
            """
            _p = {"query": query, "upload_date": upload_date, "type": type, "duration": duration, "sort_by": sort_by, "features": features, "cursor": cursor, "hd": hd, "subtitles": subtitles, "creative_commons": creative_commons, "live": live}
            return _run(lambda: client.youtube.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_search)
        @function_tool
        def scavio_youtube_shorts(query: str, sort_by: Optional[Literal["relevance", "date", "view_count", "rating"]] = None, cursor: Optional[str] = None) -> dict:
            """Search YouTube Shorts by keyword. Costs 2 credits.

            Args:
                query: The Shorts search query.
                sort_by: Sort order: relevance, date, view_count, rating.
                cursor: Pagination cursor.
            """
            _p = {"query": query, "sort_by": sort_by, "cursor": cursor}
            return _run(lambda: client.youtube.shorts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_shorts)
        @function_tool
        def scavio_youtube_suggestions(query: str, language: Optional[str] = None, region: Optional[str] = None) -> dict:
            """Fetch YouTube search autocomplete suggestions for a query. Costs 1 credit.

            Args:
                query: The partial search query to autocomplete.
                language: Two-letter language code (default en).
                region: Two-letter region code (default US).
            """
            _p = {"query": query, "language": language, "region": region}
            return _run(lambda: client.youtube.suggestions(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_suggestions)
        @function_tool
        def scavio_youtube_video(video_id: str) -> dict:
            """Fetch full details for a YouTube video (title, author, view count, description, captions, chapters). Costs 1 credit.

            Args:
                video_id: YouTube video id or a full watch URL.
            """
            _p = {"video_id": video_id}
            return _run(lambda: client.youtube.video(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_video)
        # /youtube/metadata is a deprecated alias of /youtube/video with the same
        # schema and the same handler. It is not registered as its own tool: two
        # identical tools only split the model's choice.
        @function_tool
        def scavio_youtube_comments(video_id: str, cursor: Optional[str] = None) -> dict:
            """List comments on a YouTube video. Costs 1 credit.

            Args:
                video_id: YouTube video id or a full watch URL.
                cursor: Pagination cursor.
            """
            _p = {"video_id": video_id, "cursor": cursor}
            return _run(lambda: client.youtube.comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_comments)
        @function_tool
        def scavio_youtube_comment_replies(video_id: str, reply_cursor: str, cursor: Optional[str] = None) -> dict:
            """List replies to a YouTube comment. Costs 1 credit.

            Args:
                video_id: YouTube video id or a full watch URL.
                reply_cursor: Reply cursor from a parent comment's reply_cursor.
                cursor: Pagination cursor.
            """
            _p = {"video_id": video_id, "reply_cursor": reply_cursor, "cursor": cursor}
            return _run(lambda: client.youtube.comment_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_comment_replies)
        @function_tool
        def scavio_youtube_transcript(video_id: str, language: Optional[str] = None, format: Optional[Literal["text", "srt"]] = None) -> dict:
            """Fetch a YouTube video's transcript or timed subtitles. Costs 8 credits, the most expensive YouTube tool.

            Args:
                video_id: YouTube video id or a full watch URL.
                language: Transcript language code (default en).
                format: 'text' for a plain transcript, 'srt' for timed subtitles.
            """
            _p = {"video_id": video_id, "language": language, "format": format}
            return _run(lambda: client.youtube.transcript(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_transcript)
        @function_tool
        def scavio_youtube_related(video_id: str, cursor: Optional[str] = None) -> dict:
            """List videos related to a YouTube video. Costs 1 credit.

            Args:
                video_id: YouTube video id or a full watch URL.
                cursor: Pagination cursor.
            """
            _p = {"video_id": video_id, "cursor": cursor}
            return _run(lambda: client.youtube.related(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_related)
        @function_tool
        def scavio_youtube_channel_search(query: str, cursor: Optional[str] = None) -> dict:
            """Search YouTube channels by keyword. Costs 1 credit.

            Args:
                query: The channel search query.
                cursor: Pagination cursor.
            """
            _p = {"query": query, "cursor": cursor}
            return _run(lambda: client.youtube.channel_search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_search)
        @function_tool
        def scavio_youtube_channel(channel_id: str) -> dict:
            """Fetch a YouTube channel's details (subscribers, video count, views, links). Costs 1 credit.

            Args:
                channel_id: YouTube channel id, @handle, or channel URL.
            """
            _p = {"channel_id": channel_id}
            return _run(lambda: client.youtube.channel(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel)
        @function_tool
        def scavio_youtube_channel_videos(channel_id: str, cursor: Optional[str] = None) -> dict:
            """List a YouTube channel's uploaded videos. Costs 1 credit.

            Args:
                channel_id: YouTube channel id.
                cursor: Pagination cursor.
            """
            _p = {"channel_id": channel_id, "cursor": cursor}
            return _run(lambda: client.youtube.channel_videos(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_videos)
        @function_tool
        def scavio_youtube_channel_shorts(channel_id: str, cursor: Optional[str] = None) -> dict:
            """List a YouTube channel's Shorts. Costs 1 credit.

            Args:
                channel_id: YouTube channel id.
                cursor: Pagination cursor.
            """
            _p = {"channel_id": channel_id, "cursor": cursor}
            return _run(lambda: client.youtube.channel_shorts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_shorts)
        @function_tool
        def scavio_youtube_channel_community(channel_id: str, cursor: Optional[str] = None) -> dict:
            """List a YouTube channel's community posts. Costs 1 credit.

            Args:
                channel_id: YouTube channel id.
                cursor: Pagination cursor.
            """
            _p = {"channel_id": channel_id, "cursor": cursor}
            return _run(lambda: client.youtube.channel_community(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_community)
        @function_tool
        def scavio_youtube_channel_resolve(channel: str) -> dict:
            """Resolve a YouTube @handle or channel URL to a channel id. Costs 1 credit.

            Args:
                channel: A channel @handle or channel URL.
            """
            _p = {"channel": channel}
            return _run(lambda: client.youtube.channel_resolve(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_resolve)
        @function_tool
        def scavio_youtube_streams(video_id: str) -> dict:
            """Fetch direct playable/downloadable stream URLs for a YouTube video. Costs 3 credits.

            Args:
                video_id: YouTube video id or a full watch URL.
            """
            _p = {"video_id": video_id}
            return _run(lambda: client.youtube.streams(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_streams)

    if all or enable_reddit:
        # /reddit/search takes query and cursor only. The type and sort params it
        # used to advertise were never read by the API - they were stripped on the
        # wire, so the model planned around a filter it never got. Removed.
        @function_tool
        def scavio_reddit_search(query: str, cursor: Optional[str] = None) -> dict:
            """Search Reddit posts by keyword. Costs 1 credit. Posts only: there is no type or sort filter, so rank data.results yourself.

            Args:
                query: The Reddit search query.
                cursor: Pagination cursor. Pass data.next_cursor from a prior response; data.has_more says whether another page exists.
            """
            _p = {"query": query, "cursor": cursor}
            return _run(lambda: client.reddit.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_search)
        @function_tool
        def scavio_reddit_search_suggestions(query: str) -> dict:
            """Fetch Reddit search autocomplete suggestions for a seed keyword. Costs 1 credit.

            Args:
                query: The partial search query to expand.
            """
            _p = {"query": query}
            return _run(lambda: client.reddit.search_suggestions(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_search_suggestions)
        @function_tool
        def scavio_reddit_post(url: Optional[str] = None, post_id: Optional[str] = None) -> dict:
            """Fetch one Reddit post by URL or post id. Costs 1 credit. data is a flat post object (title, text, score, upvote_ratio, num_comments, subreddit, author) and carries no comments: call scavio_reddit_post_comments for those.

            Args:
                url: Full URL of the Reddit post. Provide this or post_id.
                post_id: Post fullname (t3_...) or bare id. Provide this or url.
            """
            _p = {"url": url, "post_id": post_id}
            return _run(lambda: client.reddit.post(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_post)
        @function_tool
        def scavio_reddit_post_comments(post_id: str, sort: Optional[Literal["HOT", "NEW", "TOP", "BEST", "CONTROVERSIAL"]] = None, cursor: Optional[str] = None) -> dict:
            """List the top-level comments on a Reddit post. Costs 1 credit per page. Each comment carries a reply_cursor for scavio_reddit_comment_replies; page with data.next_cursor while data.has_more.

            Args:
                post_id: Post fullname (t3_...) or bare id.
                sort: Comment sort order: HOT, NEW, TOP, BEST, CONTROVERSIAL (server default TOP).
                cursor: Pagination cursor from a prior response.
            """
            _p = {"post_id": post_id, "sort": sort, "cursor": cursor}
            return _run(lambda: client.reddit.post_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_post_comments)
        @function_tool
        def scavio_reddit_comment_replies(post_id: str, cursor: str, sort: Optional[Literal["HOT", "NEW", "TOP", "BEST", "CONTROVERSIAL"]] = None) -> dict:
            """List the replies to one Reddit comment. Costs 1 credit per page.

            Args:
                post_id: Post fullname (t3_...) or bare id.
                cursor: The reply_cursor of a comment from scavio_reddit_post_comments. Required, and not interchangeable with next_cursor.
                sort: Comment sort order: HOT, NEW, TOP, BEST, CONTROVERSIAL (server default TOP).
            """
            _p = {"post_id": post_id, "cursor": cursor, "sort": sort}
            return _run(lambda: client.reddit.comment_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_comment_replies)
        @function_tool
        def scavio_reddit_subreddit(subreddit: str) -> dict:
            """Fetch a subreddit's metadata: title, description, subscriber count, type, NSFW flag, icon, banner, creation date. Costs 1 credit.

            Args:
                subreddit: Subreddit name, without the r/ prefix.
            """
            _p = {"subreddit": subreddit}
            return _run(lambda: client.reddit.subreddit(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_subreddit)
        @function_tool
        def scavio_reddit_subreddit_posts(subreddit: str, sort: Optional[Literal["BEST", "HOT", "NEW", "TOP", "CONTROVERSIAL", "RISING"]] = None, cursor: Optional[str] = None) -> dict:
            """List a subreddit's post feed, under data.posts. Costs 1 credit per page.

            Args:
                subreddit: Subreddit name, without the r/ prefix.
                sort: Feed sort order: BEST, HOT, NEW, TOP, CONTROVERSIAL, RISING (server default HOT).
                cursor: Pagination cursor from a prior response.
            """
            _p = {"subreddit": subreddit, "sort": sort, "cursor": cursor}
            return _run(lambda: client.reddit.subreddit_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_subreddit_posts)
        @function_tool
        def scavio_reddit_user(username: str) -> dict:
            """Fetch a redditor's profile: id, name, employee/verified flags, account type, whether they accept private messages. Costs 1 credit.

            Args:
                username: Reddit username, without the u/ prefix.
            """
            _p = {"username": username}
            return _run(lambda: client.reddit.user(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_user)
        @function_tool
        def scavio_reddit_user_posts(username: str, sort: Optional[Literal["HOT", "NEW", "TOP", "BEST", "CONTROVERSIAL"]] = None, cursor: Optional[str] = None) -> dict:
            """List a redditor's submitted posts, under data.posts. Costs 1 credit per page.

            Args:
                username: Reddit username, without the u/ prefix.
                sort: Sort order: HOT, NEW, TOP, BEST, CONTROVERSIAL (server default NEW).
                cursor: Pagination cursor from a prior response.
            """
            _p = {"username": username, "sort": sort, "cursor": cursor}
            return _run(lambda: client.reddit.user_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_user_posts)
        @function_tool
        def scavio_reddit_user_comments(username: str, sort: Optional[Literal["HOT", "NEW", "TOP", "BEST", "CONTROVERSIAL"]] = None, cursor: Optional[str] = None) -> dict:
            """List a redditor's comments, under data.comments, each with the post it belongs to. Costs 1 credit per page.

            Args:
                username: Reddit username, without the u/ prefix.
                sort: Sort order: HOT, NEW, TOP, BEST, CONTROVERSIAL (server default NEW).
                cursor: Pagination cursor from a prior response.
            """
            _p = {"username": username, "sort": sort, "cursor": cursor}
            return _run(lambda: client.reddit.user_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_user_comments)
        @function_tool
        def scavio_reddit_popular(cursor: Optional[str] = None) -> dict:
            """List the site-wide Reddit popular feed, under data.posts. Costs 1 credit per page.

            Args:
                cursor: Pagination cursor from a prior response.
            """
            _p = {"cursor": cursor}
            return _run(lambda: client.reddit.popular(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_popular)
        @function_tool
        def scavio_reddit_trending() -> dict:
            """List Reddit's current trending search queries. Takes no parameters. Costs 1 credit."""
            return _run(lambda: client.reddit.trending())
        tools.append(scavio_reddit_trending)

    if all or enable_tiktok:
        @function_tool
        def scavio_tiktok_profile(username: Optional[str] = None, sec_user_id: Optional[str] = None) -> dict:
            """Fetch a TikTok user profile by username or secUid. Costs 1 credit.

            Args:
                username: TikTok username (without @). Provide this or sec_user_id.
                sec_user_id: TikTok secUid. Provide this or username.
            """
            _p = {"username": username, "sec_user_id": sec_user_id}
            return _run(lambda: client.tiktok.profile(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_profile)
        @function_tool
        def scavio_tiktok_user_posts(sec_user_id: str, cursor: Optional[str] = None, count: Optional[int] = None, sort_type: Optional[Literal["0", "1"]] = None) -> dict:
            """List a TikTok user's posts by secUid. Costs 1 credit per page.

            Args:
                sec_user_id: TikTok secUid of the user.
                cursor: Pagination cursor, as a string (default '0').
                count: Number of posts to return (1-30).
                sort_type: '0' = latest, '1' = popular.
            """
            _p = {"sec_user_id": sec_user_id, "cursor": cursor, "count": count, "sort_type": sort_type}
            return _run(lambda: client.tiktok.user_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_user_posts)
        @function_tool
        def scavio_tiktok_video(video_id: str) -> dict:
            """Fetch a TikTok video by id. Costs 1 credit.

            Args:
                video_id: TikTok video id.
            """
            _p = {"video_id": video_id}
            return _run(lambda: client.tiktok.video(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_video)
        @function_tool
        def scavio_tiktok_video_comments(video_id: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """List comments on a TikTok video. Costs 1 credit per page.

            Args:
                video_id: TikTok video id.
                cursor: Pagination cursor, as a string (default '0').
                count: Number of comments to return (1-50).
            """
            _p = {"video_id": video_id, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.video_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_video_comments)
        @function_tool
        def scavio_tiktok_comment_replies(video_id: str, comment_id: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """List replies to a TikTok video comment. Costs 1 credit per page.

            Args:
                video_id: TikTok video id.
                comment_id: Parent comment id.
                cursor: Pagination cursor, as a string (default '0').
                count: Number of replies to return (1-50).
            """
            _p = {"video_id": video_id, "comment_id": comment_id, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.comment_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_comment_replies)
        @function_tool
        def scavio_tiktok_search_videos(keyword: str, cursor: Optional[str] = None, count: Optional[int] = None, sort_type: Optional[Literal["0", "1"]] = None, publish_time: Optional[Literal["0", "1", "7", "30", "90", "180"]] = None) -> dict:
            """Search TikTok videos by keyword. Costs 1 credit per page.

            Args:
                keyword: Search keyword.
                cursor: Pagination cursor, as a string (default '0').
                count: Number of videos to return (1-30).
                sort_type: '0' = relevance, '1' = most likes.
                publish_time: Age filter in days: '0' = all time, '1', '7', '30', '90', '180'.
            """
            _p = {"keyword": keyword, "cursor": cursor, "count": count, "sort_type": sort_type, "publish_time": publish_time}
            return _run(lambda: client.tiktok.search_videos(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_search_videos)
        @function_tool
        def scavio_tiktok_search_users(keyword: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """Search TikTok users by keyword. Costs 1 credit per page.

            Args:
                keyword: Search keyword.
                cursor: Pagination cursor, as a string (default '0').
                count: Number of users to return (1-30).
            """
            _p = {"keyword": keyword, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.search_users(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_search_users)
        @function_tool
        def scavio_tiktok_hashtag(hashtag_name: Optional[str] = None, hashtag_id: Optional[str] = None) -> dict:
            """Fetch a TikTok hashtag by name or id. Costs 1 credit.

            Args:
                hashtag_name: Hashtag name (without #). Provide this or hashtag_id.
                hashtag_id: Hashtag id. Provide this or hashtag_name.
            """
            _p = {"hashtag_name": hashtag_name, "hashtag_id": hashtag_id}
            return _run(lambda: client.tiktok.hashtag(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_hashtag)
        @function_tool
        def scavio_tiktok_hashtag_videos(hashtag_id: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """List videos for a TikTok hashtag by id. Costs 1 credit per page.

            Args:
                hashtag_id: Hashtag id.
                cursor: Pagination cursor, as a string (default '0').
                count: Number of videos to return (1-30).
            """
            _p = {"hashtag_id": hashtag_id, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.hashtag_videos(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_hashtag_videos)
        @function_tool
        def scavio_tiktok_user_followers(sec_user_id: str, count: Optional[int] = None, page_token: Optional[str] = None, min_time: Optional[int] = None) -> dict:
            """List a TikTok user's followers by secUid. Costs 1 credit per page.

            Args:
                sec_user_id: TikTok secUid of the user.
                count: Number of followers to return (1-20).
                page_token: Pagination token from a prior response.
                min_time: Minimum timestamp cursor.
            """
            _p = {"sec_user_id": sec_user_id, "count": count, "page_token": page_token, "min_time": min_time}
            return _run(lambda: client.tiktok.user_followers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_user_followers)
        @function_tool
        def scavio_tiktok_user_followings(sec_user_id: str, count: Optional[int] = None, page_token: Optional[str] = None, min_time: Optional[int] = None) -> dict:
            """List the accounts a TikTok user follows, by secUid. Costs 1 credit per page.

            Args:
                sec_user_id: TikTok secUid of the user.
                count: Number of followings to return (1-20).
                page_token: Pagination token from a prior response.
                min_time: Minimum timestamp cursor.
            """
            _p = {"sec_user_id": sec_user_id, "count": count, "page_token": page_token, "min_time": min_time}
            return _run(lambda: client.tiktok.user_followings(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_user_followings)

    if all or enable_tiktok_shop:
        # Two upstream limits shape these descriptions, and a model that does not
        # see them will build a pipeline that silently loses most of its rows:
        # only ~44% of the product ids returned by search resolve on product(),
        # and product() never carries a price. Prices come from the listing
        # tools (search, category products, shop products).
        @function_tool
        def scavio_tiktok_shop_search(search: str, cursor: Optional[str] = None) -> dict:
            """Search TikTok Shop products by keyword (US catalog). Up to 30 per page with exact prices, ratings, sold counts and shop details. Costs 1 credit per page. Page with data.next_cursor while data.has_more and dedupe by product_id. Only about 44% of these product ids resolve on scavio_tiktok_shop_product, so treat this as a standalone price source rather than the first leg of a search-then-detail pipeline.

            Args:
                search: Search keyword (1-200 characters).
                cursor: Opaque cursor from a prior response's next_cursor.
            """
            _p = {"search": search, "cursor": cursor}
            return _run(lambda: client.tiktok_shop.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_search)
        @function_tool
        def scavio_tiktok_shop_search_suggestions(search: str, region: Optional[Literal["US", "GB", "SG", "MY", "PH", "TH", "VN", "ID"]] = None) -> dict:
            """Fetch TikTok Shop keyword autocomplete and expansion for a partial query. Costs 1 credit. Suggestions are not guaranteed prefix matches: a misspelling returns typo corrections, and results can include brand and shop names.

            Args:
                search: Partial search keyword (1-100 characters).
                region: Marketplace region: US (default), GB, SG, MY, PH, TH, VN, ID.
            """
            _p = {"search": search, "region": region}
            return _run(lambda: client.tiktok_shop.search_suggestions(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_search_suggestions)
        @function_tool
        def scavio_tiktok_shop_product(product_id: str, region: Optional[Literal["US", "GB", "SG", "MY", "PH", "TH", "VN", "ID"]] = None) -> dict:
            """Fetch full TikTok Shop product detail: description, images, variants with stock, shipping, shop profile, category path and top reviews. Costs 1 credit. Two hard limits: it returns NO price (upstream masks it, so read prices from scavio_tiktok_shop_search, scavio_tiktok_shop_shop_products or scavio_tiktok_shop_category_products), and only about 44% of search product ids resolve here. A 404 is a normal outcome, not a transient error: skip that product instead of retrying, and try scavio_tiktok_shop_product_reviews, which often works for ids this cannot resolve.

            Args:
                product_id: TikTok Shop product id (6-25 digits).
                region: Marketplace region: US (default), GB, SG, MY, PH, TH, VN, ID.
            """
            _p = {"product_id": product_id, "region": region}
            return _run(lambda: client.tiktok_shop.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_product)
        @function_tool
        def scavio_tiktok_shop_product_reviews(product_id: str, page: Optional[int] = None, page_size: Optional[int] = None, sort: Optional[Literal["relevant", "recent"]] = None, rating: Optional[int] = None, has_media: Optional[bool] = None, verified_only: Optional[bool] = None, region: Optional[Literal["US", "GB", "SG", "MY", "PH", "TH", "VN", "ID"]] = None) -> dict:
            """List TikTok Shop product reviews with text, images, star histogram and verified-purchase flags, up to 200 per call. Costs 1 credit per page. total_reviews drifts between calls, so page with has_more rather than computing a page count.

            Args:
                product_id: TikTok Shop product id (6-25 digits).
                page: 1-based page number (1-500; server default 1).
                page_size: Reviews per page (1-200; server default 20).
                sort: 'relevant' (default) returns text-complete, image-heavy reviews; 'recent' is fresher but far more text-sparse.
                rating: Only reviews with this star rating (1-5).
                has_media: Only reviews with a photo or video.
                verified_only: Only verified purchases. Ignored when has_media is true; upstream allows one filter at a time.
                region: Marketplace region: US (default), GB, SG, MY, PH, TH, VN, ID.
            """
            _p = {"product_id": product_id, "page": page, "page_size": page_size, "sort": sort, "rating": rating, "has_media": has_media, "verified_only": verified_only, "region": region}
            return _run(lambda: client.tiktok_shop.product_reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_product_reviews)
        @function_tool
        def scavio_tiktok_shop_categories() -> dict:
            """Fetch the global TikTok Shop category tree: 28 top-level categories, 240 nodes, two levels deep. Category ids are identical in every region and names are always English. Takes no parameters. Costs 1 credit."""
            return _run(lambda: client.tiktok_shop.categories())
        tools.append(scavio_tiktok_shop_categories)
        @function_tool
        def scavio_tiktok_shop_category_products(category_id: str, cursor: Optional[str] = None, region: Optional[Literal["US", "GB"]] = None) -> dict:
            """List TikTok Shop products under a category id from scavio_tiktok_shop_categories, with exact prices. Costs 1 credit per page. Page size is inconsistent upstream (15 to 20), so always page with data.next_cursor. Listings are shallow: has_more turning false after a few pages is the end of the listing, not an error.

            Args:
                category_id: Category id from scavio_tiktok_shop_categories; level 1 or 2 both work.
                cursor: Opaque cursor from a prior response's next_cursor.
                region: Marketplace region. Category listings are served for US (default) and GB only.
            """
            _p = {"category_id": category_id, "cursor": cursor, "region": region}
            return _run(lambda: client.tiktok_shop.category_products(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_category_products)
        @function_tool
        def scavio_tiktok_shop_shop_products(shop_id: str, cursor: Optional[str] = None, region: Optional[Literal["US", "GB", "SG", "MY", "PH", "TH", "VN", "ID"]] = None) -> dict:
            """List a TikTok Shop seller's product catalog, 30 per page, with exact prices. Costs 1 credit per page. Shop follower count, location and shop-level rating are not here; call scavio_tiktok_shop_product for the full shop profile.

            Args:
                shop_id: TikTok Shop seller id (also called seller_id elsewhere on TikTok).
                cursor: Opaque cursor from a prior response's next_cursor.
                region: Marketplace region: US (default), GB, SG, MY, PH, TH, VN, ID.
            """
            _p = {"shop_id": shop_id, "cursor": cursor, "region": region}
            return _run(lambda: client.tiktok_shop.shop_products(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_shop_products)
        @function_tool
        def scavio_tiktok_shop_resolve(url: str) -> dict:
            """Resolve any TikTok Shop URL or share link to a product_id or shop_id, ready for the other TikTok Shop tools. Costs 1 credit. Accepts canonical product and store pages, tiktok.com/view links, affiliate share links and vt.tiktok.com short links.

            Args:
                url: A TikTok Shop URL or share link.
            """
            _p = {"url": url}
            return _run(lambda: client.tiktok_shop.resolve(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_resolve)

    if all or enable_instagram:
        # Instagram credits are per-endpoint, not flat: 10 for the hedged
        # endpoints, 8 for post and comment replies (no fallback leg to hedge),
        # 2 for user posts. Each description states its own cost so a model can
        # pick the cheap call when either would do.
        @function_tool
        def scavio_instagram_profile(username: Optional[str] = None, user_id: Optional[str] = None) -> dict:
            """Fetch an Instagram profile by username or user id. Costs 10 credits.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
            """
            _p = {"username": username, "user_id": user_id}
            return _run(lambda: client.instagram.profile(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_profile)
        @function_tool
        def scavio_instagram_user_posts(username: Optional[str] = None, user_id: Optional[str] = None, count: Optional[int] = None, cursor: Optional[str] = None) -> dict:
            """List an Instagram user's posts. Costs 2 credits, the cheapest Instagram tool.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
                count: Number of posts to return (1-50).
                cursor: Pagination cursor.
            """
            _p = {"username": username, "user_id": user_id, "count": count, "cursor": cursor}
            return _run(lambda: client.instagram.user_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_user_posts)
        @function_tool
        def scavio_instagram_user_reels(username: Optional[str] = None, user_id: Optional[str] = None, count: Optional[int] = None, cursor: Optional[str] = None) -> dict:
            """List an Instagram user's reels. Costs 10 credits.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
                count: Number of reels to return (1-50).
                cursor: Pagination cursor.
            """
            _p = {"username": username, "user_id": user_id, "count": count, "cursor": cursor}
            return _run(lambda: client.instagram.user_reels(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_user_reels)
        @function_tool
        def scavio_instagram_user_tagged(username: Optional[str] = None, user_id: Optional[str] = None, count: Optional[int] = None, cursor: Optional[str] = None) -> dict:
            """List posts an Instagram user is tagged in. Costs 10 credits.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
                count: Number of tagged posts to return (1-50).
                cursor: Pagination cursor.
            """
            _p = {"username": username, "user_id": user_id, "count": count, "cursor": cursor}
            return _run(lambda: client.instagram.user_tagged(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_user_tagged)
        @function_tool
        def scavio_instagram_user_stories(username: Optional[str] = None, user_id: Optional[str] = None) -> dict:
            """Fetch an Instagram user's current stories. Costs 10 credits.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
            """
            _p = {"username": username, "user_id": user_id}
            return _run(lambda: client.instagram.user_stories(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_user_stories)
        @function_tool
        def scavio_instagram_post(url: Optional[str] = None, media_id: Optional[str] = None, shortcode: Optional[str] = None) -> dict:
            """Fetch an Instagram post by URL, media id, or shortcode. Costs 8 credits. Video URLs are in video_versions[].url and covers in image_versions2.candidates; there is no video_url or thumbnail_url field.

            Args:
                url: Post URL. Provide one of url, media_id, or shortcode.
                media_id: Post media id.
                shortcode: Post shortcode.
            """
            _p = {"url": url, "media_id": media_id, "shortcode": shortcode}
            return _run(lambda: client.instagram.post(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_post)
        @function_tool
        def scavio_instagram_post_comments(shortcode: Optional[str] = None, url: Optional[str] = None, cursor: Optional[str] = None, sort_order: Optional[Literal["popular", "newest"]] = None) -> dict:
            """List comments on an Instagram post by shortcode or URL. Costs 10 credits.

            Args:
                shortcode: Post shortcode. Provide this or url.
                url: Post URL. Provide this or shortcode.
                cursor: Pagination cursor.
                sort_order: Comment sort order: popular or newest.
            """
            _p = {"shortcode": shortcode, "url": url, "cursor": cursor, "sort_order": sort_order}
            return _run(lambda: client.instagram.post_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_post_comments)
        @function_tool
        def scavio_instagram_comment_replies(media_id: str, comment_id: str, cursor: Optional[str] = None) -> dict:
            """List replies to an Instagram post comment. Costs 8 credits.

            Args:
                media_id: Post media id.
                comment_id: Parent comment id.
                cursor: Pagination cursor.
            """
            _p = {"media_id": media_id, "comment_id": comment_id, "cursor": cursor}
            return _run(lambda: client.instagram.comment_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_comment_replies)
        @function_tool
        def scavio_instagram_search_users(keyword: str, cursor: Optional[str] = None) -> dict:
            """Search Instagram users by keyword. Costs 10 credits.

            Args:
                keyword: Search keyword.
                cursor: Pagination cursor.
            """
            _p = {"keyword": keyword, "cursor": cursor}
            return _run(lambda: client.instagram.search_users(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_search_users)
        @function_tool
        def scavio_instagram_search_hashtags(keyword: str, cursor: Optional[str] = None) -> dict:
            """Search Instagram hashtags by keyword. Costs 10 credits.

            Args:
                keyword: Search keyword.
                cursor: Pagination cursor.
            """
            _p = {"keyword": keyword, "cursor": cursor}
            return _run(lambda: client.instagram.search_hashtags(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_search_hashtags)
        @function_tool
        def scavio_instagram_user_followers(username: Optional[str] = None, user_id: Optional[str] = None, count: Optional[int] = None, cursor: Optional[str] = None) -> dict:
            """List an Instagram user's followers. Costs 10 credits.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
                count: Number of followers to return (1-100).
                cursor: Pagination cursor.
            """
            _p = {"username": username, "user_id": user_id, "count": count, "cursor": cursor}
            return _run(lambda: client.instagram.user_followers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_user_followers)
        @function_tool
        def scavio_instagram_user_followings(username: Optional[str] = None, user_id: Optional[str] = None, count: Optional[int] = None, cursor: Optional[str] = None) -> dict:
            """List the accounts an Instagram user follows. Costs 10 credits.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
                count: Number of followings to return (1-100).
                cursor: Pagination cursor.
            """
            _p = {"username": username, "user_id": user_id, "count": count, "cursor": cursor}
            return _run(lambda: client.instagram.user_followings(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_user_followings)

    if all or enable_x:
        @function_tool
        def scavio_x_search(search: str, search_type: Optional[Literal["Top", "Latest", "People", "Photos", "Videos"]] = None, cursor: Optional[str] = None) -> dict:
            """Search X for tweets and people. Costs 1 credit per page. Each result carries the tweet id, author handle, text, language, timestamp and engagement counts. Page with data.next_cursor while data.has_more.

            Args:
                search: The X search query (1-500 characters).
                search_type: Result category: Top (default), Latest, People, Photos, Videos.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"search": search, "search_type": search_type, "cursor": cursor}
            return _run(lambda: client.x.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_search)
        @function_tool
        def scavio_x_tweet(tweet_id: str) -> dict:
            """Fetch full details for a single tweet: text, timestamp, language, engagement counts, source and reply-to reference. Costs 1 credit.

            Args:
                tweet_id: Tweet id.
            """
            _p = {"tweet_id": tweet_id}
            return _run(lambda: client.x.tweet(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_tweet)
        @function_tool
        def scavio_x_tweet_comments(tweet_id: str, rank: Optional[Literal["top", "latest"]] = None, cursor: Optional[str] = None) -> dict:
            """List the replies to a tweet, ranked or chronological. Costs 1 credit per page. Page with data.next_cursor while data.has_more.

            Args:
                tweet_id: Tweet id.
                rank: 'top' for ranked replies (default) or 'latest' for chronological.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"tweet_id": tweet_id, "rank": rank, "cursor": cursor}
            return _run(lambda: client.x.tweet_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_tweet_comments)
        @function_tool
        def scavio_x_tweet_retweeters(tweet_id: str, cursor: Optional[str] = None) -> dict:
            """List the users who retweeted a tweet, under data.retweeters. Costs 1 credit per page.

            Args:
                tweet_id: Tweet id.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"tweet_id": tweet_id, "cursor": cursor}
            return _run(lambda: client.x.tweet_retweeters(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_tweet_retweeters)
        @function_tool
        def scavio_x_user(screen_name: str) -> dict:
            """Fetch an X user's profile: handle, name, description, follower/friends/statuses/media counts, verified flag, avatar, location, website, creation date. Costs 1 credit.

            Args:
                screen_name: An X handle, without the @.
            """
            _p = {"screen_name": screen_name}
            return _run(lambda: client.x.user(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_user)
        @function_tool
        def scavio_x_user_tweets(screen_name: str, cursor: Optional[str] = None) -> dict:
            """List an X user's tweets, under data.timeline, plus data.pinned and data.user. Costs 1 credit per page. There is no has_more here: stop when next_cursor is absent or the timeline comes back empty.

            Args:
                screen_name: An X handle, without the @.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"screen_name": screen_name, "cursor": cursor}
            return _run(lambda: client.x.user_tweets(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_user_tweets)
        @function_tool
        def scavio_x_user_replies(screen_name: str, cursor: Optional[str] = None) -> dict:
            """List an X user's tweets and replies, under data.timeline. Costs 1 credit per page. There is no has_more here: stop when next_cursor is absent or the timeline comes back empty.

            Args:
                screen_name: An X handle, without the @.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"screen_name": screen_name, "cursor": cursor}
            return _run(lambda: client.x.user_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_user_replies)
        @function_tool
        def scavio_x_user_media(screen_name: str, cursor: Optional[str] = None) -> dict:
            """List an X user's media tweets (posts with photos or videos), under data.timeline. Costs 1 credit per page. There is no has_more here: stop when next_cursor is absent or the timeline comes back empty.

            Args:
                screen_name: An X handle, without the @.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"screen_name": screen_name, "cursor": cursor}
            return _run(lambda: client.x.user_media(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_user_media)
        @function_tool
        def scavio_x_user_followers(screen_name: str, cursor: Optional[str] = None) -> dict:
            """List an X user's followers. Costs 1 credit per page. Page with data.next_cursor while data.has_more.

            Args:
                screen_name: An X handle, without the @.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"screen_name": screen_name, "cursor": cursor}
            return _run(lambda: client.x.user_followers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_user_followers)
        @function_tool
        def scavio_x_user_followings(screen_name: str, cursor: Optional[str] = None) -> dict:
            """List the accounts an X user follows, under data.following (singular). Costs 1 credit per page. Page with data.next_cursor while data.has_more.

            Args:
                screen_name: An X handle, without the @.
                cursor: Pagination cursor from a prior response.
            """
            _p = {"screen_name": screen_name, "cursor": cursor}
            return _run(lambda: client.x.user_followings(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_user_followings)
        @function_tool
        def scavio_x_trending(country: Optional[str] = None) -> dict:
            """List trending topics on X for a country. Costs 1 credit.

            Args:
                country: Country name, e.g. UnitedStates (default), UnitedKingdom, Japan.
            """
            _p = {"country": country}
            return _run(lambda: client.x.trending(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_x_trending)

    if all or enable_linkedin:
        # LinkedIn credits are not uniform: profile, company and single-post reads
        # are 1, the paginated list tools are 10 per page, and job detail is 30.
        # Each description states its own cost.
        #
        # Five endpoints were dropped rather than wrapped - person/contact,
        # company/people, company/jobs, search/people and search/posts have no
        # upstream left and can only answer 410. A tool that always fails is a
        # menu item a model will still pick, burning turns on retries, so it is
        # better absent. The REST API keeps answering those paths with an
        # explicit 410 for code that already calls them.
        @function_tool
        def scavio_linkedin_person(username: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Fetch a LinkedIn member's full profile: headline, about text, location, follower and connection counts, current company, work experience, education, honours and bio links. Costs 1 credit.

            Args:
                username: Public identifier (vanity handle), e.g. williamhgates. Provide this or url.
                url: Full LinkedIn profile URL. Provide this or username.
            """
            _p = {"username": username, "url": url}
            return _run(lambda: client.linkedin.person(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_person)
        @function_tool
        def scavio_linkedin_person_about(username: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Fetch the about/overview slice of a LinkedIn member's profile: about text, headline, experience, education, honours and bio links. Costs 1 credit. Use instead of scavio_linkedin_person when only the narrative sections are needed.

            Args:
                username: Public identifier (vanity handle). Provide this or url.
                url: Full LinkedIn profile URL. Provide this or username.
            """
            _p = {"username": username, "url": url}
            return _run(lambda: client.linkedin.person_about(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_person_about)
        @function_tool
        def scavio_linkedin_person_posts(username: Optional[str] = None, url: Optional[str] = None, type: Optional[Literal["posts", "comments", "reactions"]] = None, cursor: Optional[str] = None) -> dict:
            """List a LinkedIn member's posts, with text, url, timestamps, a full reaction breakdown, comment and repost counts and attached media. Costs 10 credits per page. 50 per page; pass the previous response's next_cursor to page.

            Args:
                username: Public identifier (vanity handle). Provide this or url.
                url: Full LinkedIn profile URL. Provide this or username.
                type: Which feed: posts (default), comments (posts they commented on), or reactions (posts they reacted to).
                cursor: Opaque cursor from a prior response's next_cursor.
            """
            _p = {"username": username, "url": url, "type": type, "cursor": cursor}
            return _run(lambda: client.linkedin.person_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_person_posts)
        @function_tool
        def scavio_linkedin_company(company: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Fetch a LinkedIn company profile: about, website, industries, specialties, size, employee and follower counts, headquarters, all office locations, featured employees, similar and affiliated companies. Costs 1 credit.

            Args:
                company: Company universal name (slug), e.g. microsoft. Provide this or url.
                url: Full LinkedIn company URL. Provide this or company.
            """
            _p = {"company": company, "url": url}
            return _run(lambda: client.linkedin.company(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_company)
        @function_tool
        def scavio_linkedin_company_posts(company: Optional[str] = None, url: Optional[str] = None, cursor: Optional[str] = None) -> dict:
            """List a LinkedIn company's recent posts, in the same shape as member posts. Costs 10 credits per page. 50 per page; pass the previous response's next_cursor to page.

            Args:
                company: Company universal name (slug). Provide this or url.
                url: Full LinkedIn company URL. Provide this or company.
                cursor: Opaque cursor from a prior response's next_cursor.
            """
            _p = {"company": company, "url": url, "cursor": cursor}
            return _run(lambda: client.linkedin.company_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_company_posts)
        @function_tool
        def scavio_linkedin_search_jobs(search: str, location: Optional[str] = None, cursor: Optional[str] = None) -> dict:
            """Search LinkedIn job listings by keyword, returning title, company, location, posted time, workplace type and salary. Costs 10 credits per page. 25 per page; the provider rotates its result set, so pages overlap and repeat calls differ - dedupe by job id. Pass a company name as the search term to approximate a per-company job listing.

            Args:
                search: Search keyword, e.g. 'software engineer'.
                location: Geographic filter, e.g. 'United States'. Omit to search everywhere.
                cursor: Opaque cursor from a prior response's next_cursor.
            """
            _p = {"search": search, "location": location, "cursor": cursor}
            return _run(lambda: client.linkedin.search_jobs(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_search_jobs)
        @function_tool
        def scavio_linkedin_job(job_id: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Fetch full details for one LinkedIn job listing, including the hiring company. Costs 30 credits, the most expensive Scavio tool: prefer the fields already returned by scavio_linkedin_search_jobs when they are enough. Roughly one job id in five has no detail record upstream and returns an unbilled 404.

            Args:
                job_id: Job listing id. Provide this or url.
                url: Full LinkedIn job URL. Provide this or job_id.
            """
            _p = {"job_id": job_id, "url": url}
            return _run(lambda: client.linkedin.job(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_job)
        @function_tool
        def scavio_linkedin_post(post_id: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Fetch full details for one LinkedIn post: body text, timestamp, hashtags, links, media, like and comment counts, tagged companies and people, top visible comments and the author. Costs 1 credit.

            Args:
                post_id: Post id or activity urn. Provide this or url.
                url: Full LinkedIn post URL. Provide this or post_id.
            """
            _p = {"post_id": post_id, "url": url}
            return _run(lambda: client.linkedin.post(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_post)
        @function_tool
        def scavio_linkedin_post_comments(post_id: Optional[str] = None, url: Optional[str] = None, page: Optional[int] = None) -> dict:
            """List the comments on a LinkedIn post, each with the commenter and any nested replies. Costs 10 credits per page. Paginated by a 1-based page number, not a cursor; page size varies, so keep incrementing until a page comes back empty.

            Args:
                post_id: Post id or activity urn. Provide this or url.
                url: Full LinkedIn post URL. Provide this or post_id.
                page: 1-based page number (default 1).
            """
            _p = {"post_id": post_id, "url": url, "page": page}
            return _run(lambda: client.linkedin.post_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_linkedin_post_comments)

    if all or enable_threads:
        @function_tool
        def scavio_threads_profile(user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
            """Profile details for a Threads user. Costs 2 credits addressed by user_id and 4 by username; pass user_id whenever you have it.

            Args:
                user_id: Numeric Threads user id, e.g. '63625256886'. The cheap path: 2 credits.
                username: Threads handle without the @ (1-60 characters). Costs 2 extra credits (4 total): the upstream handle lookup is down, so the handle is resolved through people search first. Pass user_id instead to avoid that.
            """
            _p = {"user_id": user_id, "username": username}
            return _run(lambda: client.threads.profile(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_threads_profile)
        @function_tool
        def scavio_threads_user_posts(user_id: Optional[str] = None, username: Optional[str] = None, cursor: Optional[str] = None) -> dict:
            """A user's Threads posts, cursor-paginated via next_cursor. Costs 2 credits addressed by user_id and 4 by username.

            Args:
                user_id: Numeric Threads user id, e.g. '63625256886'. The cheap path: 2 credits.
                username: Threads handle without the @ (1-60 characters). Costs 2 extra credits (4 total) because the handle has to be resolved through people search first.
                cursor: Pagination cursor from a prior response's next_cursor. Omit for the first page.
            """
            _p = {"user_id": user_id, "username": username, "cursor": cursor}
            return _run(lambda: client.threads.user_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_threads_user_posts)
        @function_tool
        def scavio_threads_user_replies(user_id: Optional[str] = None, username: Optional[str] = None, cursor: Optional[str] = None) -> dict:
            """A user's Threads replies, cursor-paginated via next_cursor. Costs 2 credits addressed by user_id and 4 by username.

            Args:
                user_id: Numeric Threads user id, e.g. '63625256886'. The cheap path: 2 credits.
                username: Threads handle without the @ (1-60 characters). Costs 2 extra credits (4 total) because the handle has to be resolved through people search first.
                cursor: Pagination cursor from a prior response's next_cursor. Omit for the first page.
            """
            _p = {"user_id": user_id, "username": username, "cursor": cursor}
            return _run(lambda: client.threads.user_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_threads_user_replies)
        @function_tool
        def scavio_threads_post(post_id: Optional[str] = None, url: Optional[str] = None) -> dict:
            """A single Threads post, addressed by post_id or by its threads.net URL. Costs 2 credits. Threads is body-priced by identifier, but this endpoint has no username form, so it is always 2.

            Args:
                post_id: Threads post id, e.g. '3349029093483693129'.
                url: Full threads.net post URL (e.g. 'https://www.threads.net/@natgeo/post/C8xY'), as an alternative to post_id.
            """
            _p = {"post_id": post_id, "url": url}
            return _run(lambda: client.threads.post(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_threads_post)
        @function_tool
        def scavio_threads_post_comments(post_id: str, cursor: Optional[str] = None) -> dict:
            """Replies to a Threads post, cursor-paginated via next_cursor. Post-keyed only: there is no username form, so this endpoint always costs 2 credits.

            Args:
                post_id: Threads post id, e.g. '3349029093483693129'.
                cursor: Pagination cursor from a prior response's next_cursor. Omit for the first page.
            """
            _p = {"post_id": post_id, "cursor": cursor}
            return _run(lambda: client.threads.post_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_threads_post_comments)
        @function_tool
        def scavio_threads_search_users(query: str) -> dict:
            """Search Threads profiles by name or handle. This is the only search Threads exposes - there is no post or content search - and it returns a single unpaginated page. Costs 2 credits. Threads is body-priced by identifier, but this endpoint has no username form, so it is always 2.

            Args:
                query: Name or handle to search for (1-200 characters).
            """
            _p = {"query": query}
            return _run(lambda: client.threads.search_users(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_threads_search_users)

    if all or enable_kuaishou:
        @function_tool
        def scavio_kuaishou_profile(user_id: str) -> dict:
            """Profile details for a Kuaishou user. Costs 10 credits, the dearest single-object call on the platform.

            Args:
                user_id: Kuaishou user id (non-empty); get one from user_resolve or search_users.
            """
            _p = {"user_id": user_id}
            return _run(lambda: client.kuaishou.profile(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_profile)
        @function_tool
        def scavio_kuaishou_user_posts(user_id: str, cursor: Optional[str] = None) -> dict:
            """A Kuaishou user's top posts, cursor-paginated via next_cursor. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform.

            Args:
                user_id: Kuaishou user id (non-empty); get one from user_resolve or search_users.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
            """
            _p = {"user_id": user_id, "cursor": cursor}
            return _run(lambda: client.kuaishou.user_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_user_posts)
        @function_tool
        def scavio_kuaishou_user_live(user_id: str) -> dict:
            """A Kuaishou user's current live-stream status. Not paginated. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform.

            Args:
                user_id: Kuaishou user id (non-empty); get one from user_resolve or search_users.
            """
            _p = {"user_id": user_id}
            return _run(lambda: client.kuaishou.user_live(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_user_live)
        @function_tool
        def scavio_kuaishou_user_resolve(share_link: str) -> dict:
            """Turns a Kuaishou share link into a user id. Only kuaishou.com and v.kuaishou.com links are accepted; Kwai international (kwai.com) is not served upstream. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform.

            Args:
                share_link: A kuaishou.com or v.kuaishou.com URL; kwai.com links are rejected.
            """
            _p = {"share_link": share_link}
            return _run(lambda: client.kuaishou.user_resolve(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_user_resolve)
        @function_tool
        def scavio_kuaishou_video(photo_id: Optional[str] = None, url: Optional[str] = None) -> dict:
            """A single Kuaishou video by photo id or URL. Provide photo_id or url. Costs 2 credits.

            Args:
                photo_id: Kuaishou photo (video) id, non-empty.
                url: Full kuaishou.com video URL, as an alternative to photo_id.
            """
            _p = {"photo_id": photo_id, "url": url}
            return _run(lambda: client.kuaishou.video(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_video)
        @function_tool
        def scavio_kuaishou_video_comments(photo_id: str, cursor: Optional[str] = None) -> dict:
            """Comments on a Kuaishou video, cursor-paginated via next_cursor. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform.

            Args:
                photo_id: Kuaishou photo (video) id, non-empty.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
            """
            _p = {"photo_id": photo_id, "cursor": cursor}
            return _run(lambda: client.kuaishou.video_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_video_comments)
        @function_tool
        def scavio_kuaishou_comment_replies(photo_id: str, root_comment_id: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """Replies under a root comment on a Kuaishou video, cursor-paginated via next_cursor; count sizes the page (1-50). Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform.

            Args:
                photo_id: Kuaishou photo (video) id, non-empty.
                root_comment_id: Id of the top-level comment whose replies you want, from video_comments.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
                count: Replies per page, 1-50. Omit to use the upstream default.
            """
            _p = {"photo_id": photo_id, "root_comment_id": root_comment_id, "cursor": cursor, "count": count}
            return _run(lambda: client.kuaishou.comment_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_comment_replies)
        @function_tool
        def scavio_kuaishou_videos_batch(photo_ids: list) -> dict:
            """Several Kuaishou videos in one call, hard-capped at 20 photo ids. Costs 40 credits, the dearest call on the platform.

            Args:
                photo_ids: Kuaishou photo (video) ids, 1-20 per call; more than 20 is rejected.
            """
            _p = {"photo_ids": photo_ids}
            return _run(lambda: client.kuaishou.videos_batch(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_videos_batch)
        @function_tool
        def scavio_kuaishou_search(keyword: str, cursor: Optional[str] = None) -> dict:
            """Mixed-result search across Kuaishou, cursor-paginated via next_cursor. Costs 10 credits per page.

            Args:
                keyword: Search keyword, 1-200 characters.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
            """
            _p = {"keyword": keyword, "cursor": cursor}
            return _run(lambda: client.kuaishou.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_search)
        @function_tool
        def scavio_kuaishou_search_videos(keyword: str, cursor: Optional[str] = None) -> dict:
            """Kuaishou video search results, cursor-paginated via next_cursor. Costs 10 credits per page.

            Args:
                keyword: Search keyword, 1-200 characters.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
            """
            _p = {"keyword": keyword, "cursor": cursor}
            return _run(lambda: client.kuaishou.search_videos(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_search_videos)
        @function_tool
        def scavio_kuaishou_search_users(keyword: str, cursor: Optional[str] = None) -> dict:
            """Kuaishou user search results, cursor-paginated via next_cursor. Costs 10 credits per page.

            Args:
                keyword: Search keyword, 1-200 characters.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
            """
            _p = {"keyword": keyword, "cursor": cursor}
            return _run(lambda: client.kuaishou.search_users(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_search_users)
        @function_tool
        def scavio_kuaishou_search_live(keyword: str, cursor: Optional[str] = None) -> dict:
            """Kuaishou live-stream search results, cursor-paginated via next_cursor. Costs 10 credits per page.

            Args:
                keyword: Search keyword, 1-200 characters.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
            """
            _p = {"keyword": keyword, "cursor": cursor}
            return _run(lambda: client.kuaishou.search_live(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_search_live)
        @function_tool
        def scavio_kuaishou_tag_feed(tag: str, cursor: Optional[str] = None) -> dict:
            """Posts under a Kuaishou hashtag, cursor-paginated via next_cursor. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform.

            Args:
                tag: Hashtag text without the leading '#', 1-200 characters.
                cursor: Opaque next_cursor from a prior response; omit for the first page.
            """
            _p = {"tag": tag, "cursor": cursor}
            return _run(lambda: client.kuaishou.tag_feed(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_tag_feed)
        @function_tool
        def scavio_kuaishou_trending(board: Optional[Literal["hot", "live", "shopping", "brand", "music"]] = None) -> dict:
            """Kuaishou hot / live / shopping / brand / music leaderboards. One board per call, not paginated. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform.

            Args:
                board: Leaderboard to return; defaults to 'hot' when omitted. One of: hot, live, shopping, brand, music.
            """
            _p = {"board": board}
            return _run(lambda: client.kuaishou.trending(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_kuaishou_trending)

    if all or enable_ebay:
        @function_tool
        def scavio_ebay_search(query: Optional[str] = None, seller: Optional[str] = None, page: Optional[int] = None, sort_by: Optional[Literal["best_match", "ending_soonest", "newly_listed", "price_low", "price_high"]] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, condition: Optional[Literal["new", "open_box", "refurbished", "used", "for_parts"]] = None, buying_format: Optional[Literal["auction", "buy_it_now", "best_offer"]] = None, free_shipping: Optional[bool] = None, sold: Optional[bool] = None, category_id: Optional[str] = None, per_page: Optional[Literal[60, 120, 240]] = None) -> dict:
            """Search live or SOLD eBay listings: price, condition, bids, shipping, seller, feedback. Provide query or seller; per_page accepts only 60, 120 or 240. Costs 1 credit.

            Args:
                query: Keyword to search (1-500 characters). Optional: a seller-only search pages that seller's whole catalogue.
                seller: Restrict results to one seller's listings (1-64 characters), as in ebay.com/usr/<name>. Can be sent with no query.
                page: Results page, 1-based.
                sort_by: Result sort order. Defaults to 'best_match'. eBay's 'Distance: nearest first' is deliberately unsupported (it ranks against our proxy exit, not the caller). One of: best_match, ending_soonest, newly_listed, price_low, price_high.
                min_price: Minimum price, inclusive. Must be 0 or greater.
                max_price: Maximum price, inclusive. Must be 0 or greater.
                condition: Item condition filter. 'refurbished' is eBay's parent condition, not one of its three graded tiers. One of: new, open_box, refurbished, used, for_parts.
                buying_format: Listing format: auction, fixed price (buy_it_now), or fixed price accepting offers (best_offer).
                free_shipping: Only listings with free shipping.
                sold: Search completed listings that actually SOLD, for price research. eBay publishes no headline count on this view, so total_results is null.
                category_id: eBay category id; must be numeric (e.g. '112529'). An unrecognised id returns the UNFILTERED set under a 200.
                per_page: Listings per page: 60, 120 or 240 only. Defaults to 60; eBay silently falls back to 60 for anything else.
            """
            _p = {"query": query, "seller": seller, "page": page, "sort_by": sort_by, "min_price": min_price, "max_price": max_price, "condition": condition, "buying_format": buying_format, "free_shipping": free_shipping, "sold": sold, "category_id": category_id, "per_page": per_page}
            return _run(lambda: client.ebay.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_ebay_search)
        @function_tool
        def scavio_ebay_product(item_id: str) -> dict:
            """One eBay listing in full: price, condition, images, item specifics, shipping, returns, auction state, seller. Costs 1 credit.

            Args:
                item_id: eBay item number (e.g. '168591664725'), or a full ebay.com/itm/... listing URL; tracking parameters on a pasted URL are discarded.
            """
            _p = {"item_id": item_id}
            return _run(lambda: client.ebay.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_ebay_product)
        @function_tool
        def scavio_ebay_seller(seller: str) -> dict:
            """eBay seller profile card: store name, feedback score and %, items sold, followers, location, categories. Profile only: page a catalogue with search(seller=...). Costs 1 credit.

            Args:
                seller: eBay username as it appears in ebay.com/usr/<name> (1-64 characters), which is what seller_name on a search or product result returns.
            """
            _p = {"seller": seller}
            return _run(lambda: client.ebay.seller(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_ebay_seller)

    if all or enable_target:
        @function_tool
        def scavio_target_search(keyword: str, page: Optional[int] = None, count: Optional[int] = None, sort: Optional[Literal["relevance", "featured", "price_low", "price_high", "rating_high", "best_seller", "newest"]] = None, store_id: Optional[str] = None) -> dict:
            """Search Target.com, the US retailer: prices, ratings, badges and promotions. Up to 28 results per page; rendered upstream, so expect around 9 seconds. Costs 1 credit.

            Args:
                keyword: Search keyword (1-500 characters).
                page: Results page, 1-based.
                count: Results per page, 1-28. Defaults to 24; Target rejects anything above 28 outright.
                sort: Result sort order. Defaults to 'relevance'. One of: relevance, featured, price_low, price_high, rating_high, best_seller, newest.
                store_id: Numeric Target store id whose prices and availability the response reflects. Defaults to '3991', the store target.com uses with no store context.
            """
            _p = {"keyword": keyword, "page": page, "count": count, "sort": sort, "store_id": store_id}
            return _run(lambda: client.target.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_target_search)
        @function_tool
        def scavio_target_category(category_id: str, page: Optional[int] = None, count: Optional[int] = None, sort: Optional[Literal["relevance", "featured", "price_low", "price_high", "rating_high", "best_seller", "newest"]] = None, store_id: Optional[str] = None) -> dict:
            """Products in a Target category, same shape as search plus the category breadcrumb. Up to 28 per page; the slowest Target endpoint at around 37 seconds. Costs 1 credit.

            Args:
                category_id: Target category id: the segment after 'N-' in a target.com /c/ URL (target.com/c/apple/-/N-5xtg6 -> '5xtg6').
                page: Results page, 1-based.
                count: Results per page, 1-28. Defaults to 24; Target rejects anything above 28 outright.
                sort: Result sort order. Defaults to 'relevance'. One of: relevance, featured, price_low, price_high, rating_high, best_seller, newest.
                store_id: Numeric Target store id whose prices and availability the response reflects. Defaults to '3991'.
            """
            _p = {"category_id": category_id, "page": page, "count": count, "sort": sort, "store_id": store_id}
            return _run(lambda: client.target.category(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_target_category)
        @function_tool
        def scavio_target_product(tcin: str, store_id: Optional[str] = None) -> dict:
            """Target product details by TCIN: price, rating, images, specifications, variants, return policy, fulfillment. seller_id/seller_name are null for stock sold by Target. Costs 1 credit.

            Args:
                tcin: Target catalog id (tcin, e.g. '1010453160'). A colour/size child tcin is answered by its variation parent, with the child present in 'variants'.
                store_id: Numeric Target store id whose prices and availability the response reflects. Defaults to '3991'.
            """
            _p = {"tcin": tcin, "store_id": store_id}
            return _run(lambda: client.target.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_target_product)
        @function_tool
        def scavio_target_reviews(tcin: str, limit: Optional[int] = None, store_id: Optional[str] = None) -> dict:
            """Target reviews with the rating breakdown, per-attribute averages and guest photos. 8 review bodies maximum and no paging; expect around 40 seconds. Costs 1 credit.

            Args:
                tcin: Target catalog id (tcin, e.g. '1010453160').
                limit: Trim the returned reviews to at most this many (1 or greater). Target publishes 8 anonymously and offers no paging, so this only trims.
                store_id: Numeric Target store id whose prices and availability the response reflects. Defaults to '3991'.
            """
            _p = {"tcin": tcin, "limit": limit, "store_id": store_id}
            return _run(lambda: client.target.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_target_reviews)

    if all or enable_home_depot:
        @function_tool
        def scavio_home_depot_search(query: str, page: Optional[int] = None, sort_by: Optional[Literal["best_match", "top_sellers", "top_rated", "price_low", "price_high"]] = None, min_price: Optional[float] = None, max_price: Optional[float] = None) -> dict:
            """Search Home Depot: price and promotions, brand and model, ratings, badges, per-store pickup/delivery. Page size is fixed at 12 and cannot be changed. Costs 2 credits.

            Args:
                query: Search keyword (1-500 characters).
                page: Results page, 1-based. Home Depot serves 12 products per page and offers no way to change that, so paging is the only way to read further.
                sort_by: Result sort order. Defaults to 'best_match'. Closed enum: Home Depot answers an unknown sort with an empty page that is still billed. 'Newest' is absent - it is rejected on keyword search. One of: best_match, top_sellers, top_rated, price_low, price_high.
                min_price: Minimum price, inclusive. Must be 0 or greater.
                max_price: Maximum price, inclusive. Must be 0 or greater.
            """
            _p = {"query": query, "page": page, "sort_by": sort_by, "min_price": min_price, "max_price": max_price}
            return _run(lambda: client.home_depot.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_home_depot_search)
        @function_tool
        def scavio_home_depot_product(item_id: str) -> dict:
            """Full Home Depot item detail: pricing, images and videos, spec table, dimensions, bullets, documents, return policy. Carries a 10-review preview only. Costs 2 credits.

            Args:
                item_id: Home Depot item id (e.g. '325479354'), or a full homedepot.com/p/... product URL; tracking parameters on a pasted URL are discarded.
            """
            _p = {"item_id": item_id}
            return _run(lambda: client.home_depot.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_home_depot_product)
        @function_tool
        def scavio_home_depot_reviews(item_id: str, page: Optional[int] = None) -> dict:
            """One page of full Home Depot review bodies, the rating distribution, per-attribute ratings, photos and seller responses. 30 reviews per page. Costs 2 credits.

            Args:
                item_id: Home Depot item id (e.g. '325479354'), or a full homedepot.com/p/... product URL; tracking parameters on a pasted URL are discarded.
                page: Reviews page, 1-based. 30 reviews per page; 'total_pages' in the response is the last one that exists, and asking past it is a 404.
            """
            _p = {"item_id": item_id, "page": page}
            return _run(lambda: client.home_depot.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_home_depot_reviews)

    if all or enable_zillow:
        @function_tool
        def scavio_zillow_search(location: str, listing_status: Optional[Literal["for_sale", "for_rent", "sold"]] = None, page: Optional[int] = None, sort: Optional[Literal["relevance", "recommended", "newest", "price_low", "price_high", "payment_low", "payment_high", "beds", "baths", "sqft", "lot_size", "zestimate_low", "zestimate_high", "recent_change"]] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, beds_min: Optional[int] = None, beds_max: Optional[int] = None, baths_min: Optional[float] = None, baths_max: Optional[float] = None, sqft_min: Optional[int] = None, sqft_max: Optional[int] = None, lot_size_min: Optional[int] = None, lot_size_max: Optional[int] = None, year_built_min: Optional[int] = None, year_built_max: Optional[int] = None, max_hoa: Optional[float] = None, home_type: Optional[Literal["houses", "townhomes", "multi_family", "condos", "apartments", "manufactured", "lots_land"]] = None, days_on_zillow: Optional[Literal["1", "7", "14", "30", "90", "6m", "12m", "24m", "36m"]] = None, keywords: Optional[str] = None, has_pool: Optional[bool] = None, has_garage: Optional[bool] = None, has_air_conditioning: Optional[bool] = None, is_waterfront: Optional[bool] = None, has_basement: Optional[bool] = None, is_new_construction: Optional[bool] = None, has_open_house: Optional[bool] = None, price_reduced: Optional[bool] = None, is_3d_tour: Optional[bool] = None) -> dict:
            """Zillow listings in a region: price, beds, baths, living area, Zestimate, coordinates, images, days on market. A bare ZIP works alone but cannot be combined with a filter or a sort. Costs 1 credit.

            Args:
                location: Region to search (1-200 characters): a Zillow slug ('austin-tx'), a human form ('Austin, TX'), a ZIP, or a pasted zillow.com search URL. A ZIP works alone but cannot be combined with a filter or sort; an unresolvable region is a 404.
                listing_status: Which listings to return. Defaults to 'for_sale'. One of: for_sale, for_rent, sold.
                page: Results page, 1-based.
                sort: Result sort order. Sorts that rank against a signed-in profile (saved/featured/personalised) are unsupported - we are never signed in. One of: relevance, recommended, newest, price_low, price_high, payment_low, payment_high, beds, baths, sqft, lot_size, zestimate_low, zestimate_high, recent_change.
                min_price: Minimum price, inclusive (0 or greater). On listing_status='for_rent' this is MONTHLY RENT - Zillow files rent under its payment filter.
                max_price: Maximum price, inclusive (0 or greater). On listing_status='for_rent' this is MONTHLY RENT.
                beds_min: Minimum bedrooms; whole number, 0 or greater.
                beds_max: Maximum bedrooms; whole number, 0 or greater.
                baths_min: Minimum bathrooms, 0 or greater. Half-baths are allowed (1.5).
                baths_max: Maximum bathrooms, 0 or greater. Half-baths are allowed (1.5).
                sqft_min: Minimum living area in square feet; whole number, 0 or greater.
                sqft_max: Maximum living area in square feet; whole number, 0 or greater.
                lot_size_min: Minimum lot size in square feet; whole number, 0 or greater.
                lot_size_max: Maximum lot size in square feet; whole number, 0 or greater.
                year_built_min: Earliest year built; whole number, 0 or greater.
                year_built_max: Latest year built; whole number, 0 or greater.
                max_hoa: Maximum monthly HOA fee in dollars, 0 or greater.
                home_type: Property type filter. One of: houses, townhomes, multi_family, condos, apartments, manufactured, lots_land.
                days_on_zillow: Listed - or, with listing_status='sold', sold - within the last N days. Closed enum: an unrecognised value returns the UNFILTERED set under a 200. One of: 1, 7, 14, 30, 90, 6m, 12m, 24m, 36m.
                keywords: Free-text match against the listing description (1-200 characters).
                has_pool: Only listings with a pool.
                has_garage: Only listings with a garage.
                has_air_conditioning: Only listings with air conditioning.
                is_waterfront: Only waterfront listings.
                has_basement: Only listings with a basement.
                is_new_construction: Only new-construction listings.
                has_open_house: Only listings with an upcoming open house.
                price_reduced: Only listings whose price was reduced.
                is_3d_tour: Only listings with a 3D tour.
            """
            _p = {"location": location, "listing_status": listing_status, "page": page, "sort": sort, "min_price": min_price, "max_price": max_price, "beds_min": beds_min, "beds_max": beds_max, "baths_min": baths_min, "baths_max": baths_max, "sqft_min": sqft_min, "sqft_max": sqft_max, "lot_size_min": lot_size_min, "lot_size_max": lot_size_max, "year_built_min": year_built_min, "year_built_max": year_built_max, "max_hoa": max_hoa, "home_type": home_type, "days_on_zillow": days_on_zillow, "keywords": keywords, "has_pool": has_pool, "has_garage": has_garage, "has_air_conditioning": has_air_conditioning, "is_waterfront": is_waterfront, "has_basement": has_basement, "is_new_construction": is_new_construction, "has_open_house": has_open_house, "price_reduced": price_reduced, "is_3d_tour": is_3d_tour}
            return _run(lambda: client.zillow.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_zillow_search)
        @function_tool
        def scavio_zillow_property(zpid: str) -> dict:
            """Full Zillow listing: price and price history, Zestimate, tax history, RESO facts, rooms, schools, open houses, photos. Rental buildings return floor plans instead. Costs 1 credit.

            Args:
                zpid: Zillow property id (e.g. '29414894'), a full /homedetails/ URL, or a rental building URL (zillow.com/apartments/...). The building form is required for buildings: they have no zpid a caller can see.
            """
            _p = {"zpid": zpid}
            return _run(lambda: client.zillow.property(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_zillow_property)
        @function_tool
        def scavio_zillow_agent_reviews(screen_name: str) -> dict:
            """A Zillow AGENT's profile and reviews: rating, bodies with sub-ratings, specialties, licenses, service areas, sales counts. Zillow server-renders the first five. Costs 1 credit.

            Args:
                screen_name: Zillow agent profile screen name as it appears in zillow.com/profile/<name>/ (1-200 characters, may contain spaces), or a full profile URL.
            """
            _p = {"screen_name": screen_name}
            return _run(lambda: client.zillow.agent_reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_zillow_agent_reviews)

    if all or enable_booking:
        @function_tool
        def scavio_booking_search(destination: Optional[str] = None, dest_id: Optional[str] = None, dest_type: Optional[Literal["city", "region", "country", "district", "landmark", "airport", "hotel"]] = None, page: Optional[int] = None, sort_by: Optional[Literal["popularity", "price_low", "price_high", "stars_high", "stars_low", "stars_and_price", "distance", "review_score"]] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, stars: Optional[list] = None, min_review_score: Optional[Literal["6", "7", "8", "9"]] = None, property_type: Optional[Literal["apartments", "hostels", "hotels", "motels", "resorts", "bed_and_breakfasts", "villas", "campgrounds", "vacation_homes", "lodges", "homestays"]] = None, free_cancellation: Optional[bool] = None, no_prepayment: Optional[bool] = None, breakfast_included: Optional[bool] = None, checkin: Optional[str] = None, checkout: Optional[str] = None, adults: Optional[int] = None, children_ages: Optional[list] = None, rooms: Optional[int] = None, currency: Optional[str] = None) -> dict:
            """Booking.com properties for a destination and stay: live nightly price, review score, star rating, location, room type, deal badges. 25 properties per page. Provide destination or dest_id. Costs 1 credit.

            Args:
                destination: Destination to search, e.g. 'Paris' (1-200 characters). Required unless dest_id is given.
                dest_id: Numeric Booking.com destination id, as an alternative to destination.
                dest_type: What dest_id refers to. Requires dest_id and is rejected without it, because Booking silently ignores a lone dest_type. One of: city, region, country, district, landmark, airport, hotel.
                page: Results page, 1-based. 25 properties per page, 1 credit each.
                sort_by: Result sort order (default 'popularity'). One of: popularity, price_low, price_high, stars_high, stars_low, stars_and_price, distance, review_score.
                min_price: Minimum price PER NIGHT in `currency`, >= 0. Must not exceed max_price.
                max_price: Maximum price PER NIGHT in `currency`, >= 0.
                stars: Star ratings to include, each 1-5, 1-5 values, OR'd together (e.g. [4, 5]).
                min_review_score: Minimum guest review score. Only '6', '7', '8' and '9' exist upstream; any other threshold is silently dropped.
                property_type: Accommodation type by name, or a raw numeric Booking accommodation-type id (>= 1).
                free_cancellation: Only properties offering free cancellation.
                no_prepayment: Only properties that take no prepayment.
                breakfast_included: Only rates that include breakfast.
                checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout: a lone checkin is ignored and Booking prices a default range of its own.
                checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent together with it.
                adults: Adult guests, >= 1 (default 2).
                children_ages: AGES of accompanying children, each 0-17, max 10 entries. Ages, not a count.
                rooms: Rooms required, >= 1 (default 1).
                currency: ISO 4217 currency for prices, 3 letters (default 'USD'). Without it Booking prices off the proxy exit and identical requests disagree.
            """
            _p = {"destination": destination, "dest_id": dest_id, "dest_type": dest_type, "page": page, "sort_by": sort_by, "min_price": min_price, "max_price": max_price, "stars": stars, "min_review_score": min_review_score, "property_type": property_type, "free_cancellation": free_cancellation, "no_prepayment": no_prepayment, "breakfast_included": breakfast_included, "checkin": checkin, "checkout": checkout, "adults": adults, "children_ages": children_ages, "rooms": rooms, "currency": currency}
            return _run(lambda: client.booking.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_booking_search)
        @function_tool
        def scavio_booking_hotel(hotel: str, country_code: Optional[str] = None, checkin: Optional[str] = None, checkout: Optional[str] = None, adults: Optional[int] = None, children_ages: Optional[list] = None, rooms: Optional[int] = None, currency: Optional[str] = None) -> dict:
            """One Booking.com property in full: rooms and rate plans, facilities, house rules, check-in windows, policies, images, location and review scores, priced for the stay asked for. Chaining the `url` a search row returns is cheaper than a bare slug. Costs 1 credit.

            Args:
                hotel: Booking.com property URL or the bare page slug (1-500 characters); query params are discarded.
                country_code: Two-letter country code for the property page (default 'us'). Only consulted for a bare slug, where a wrong one is a real, BILLED 404.
                checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout; omitting both prices a two-night range Booking chose, echoed back in the response.
                checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent together with it.
                adults: Adult guests, >= 1 (default 2).
                children_ages: AGES of accompanying children, each 0-17, max 10 entries. Ages, not a count.
                rooms: Rooms required, >= 1 (default 1).
                currency: ISO 4217 currency for prices, 3 letters (default 'USD'). Without it Booking prices off the proxy exit and identical requests disagree.
            """
            _p = {"hotel": hotel, "country_code": country_code, "checkin": checkin, "checkout": checkout, "adults": adults, "children_ages": children_ages, "rooms": rooms, "currency": currency}
            return _run(lambda: client.booking.hotel(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_booking_hotel)
        @function_tool
        def scavio_booking_reviews(hotel: str, country_code: Optional[str] = None, checkin: Optional[str] = None, checkout: Optional[str] = None, adults: Optional[int] = None, children_ages: Optional[list] = None, rooms: Optional[int] = None, currency: Optional[str] = None) -> dict:
            """Booking.com guest reviews for a property with the score breakdown by category and Booking's own praise/complaint summary. No page param: total_count is the whole review history, count is what this response holds. Costs 1 credit.

            Args:
                hotel: Booking.com property URL or the bare page slug (1-500 characters); query params are discarded.
                country_code: Two-letter country code for the property page (default 'us'). Only consulted for a bare slug, where a wrong one is a real, BILLED 404.
                checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout; it prices the stay the review page is rendered for.
                checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent together with it.
                adults: Adult guests, >= 1 (default 2).
                children_ages: AGES of accompanying children, each 0-17, max 10 entries. Ages, not a count.
                rooms: Rooms required, >= 1 (default 1).
                currency: ISO 4217 currency for prices, 3 letters (default 'USD').
            """
            _p = {"hotel": hotel, "country_code": country_code, "checkin": checkin, "checkout": checkout, "adults": adults, "children_ages": children_ages, "rooms": rooms, "currency": currency}
            return _run(lambda: client.booking.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_booking_reviews)

    if all or enable_tripadvisor:
        @function_tool
        def scavio_tripadvisor_locations(query: str, limit: Optional[int] = None) -> dict:
            """START HERE: resolve a place or business NAME to the TripAdvisor geo_id / location_id pair every other TripAdvisor endpoint is keyed by. Up to 20 rows. Costs 2 credits.

            Args:
                query: Place or business name to resolve (1-120 characters).
                limit: Rows to return, 1-20 (default 12). Sizes the response only; there is no paging here.
            """
            _p = {"query": query, "limit": limit}
            return _run(lambda: client.tripadvisor.locations(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tripadvisor_locations)
        @function_tool
        def scavio_tripadvisor_search(geo_id: Optional[str] = None, category: Optional[Literal["restaurants", "hotels", "attractions"]] = None, page: Optional[int] = None, url: Optional[str] = None) -> dict:
            """Restaurants, hotels or attractions in a TripAdvisor geo, TripAdvisor-ranked: rating, review count, price band, address, coordinates, phone, hours, Travelers' Choice badge; each row carries the location_id + geo_id pair. 30 locations per page. Provide geo_id or url. Costs 2 credits.

            Args:
                geo_id: TripAdvisor geo id (1-500 characters): 30196, g30196, or a URL carrying one. Required unless url is given.
                category: Listing family to search (default 'restaurants'). One of: restaurants, hotels, attractions.
                page: Results page, 1-based. 30 locations per page; a page beyond the last is a 404, not an empty result.
                url: Full tripadvisor.com listing URL (1-500 characters), as an alternative to geo_id; country sites are accepted.
            """
            _p = {"geo_id": geo_id, "category": category, "page": page, "url": url}
            return _run(lambda: client.tripadvisor.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tripadvisor_search)
        @function_tool
        def scavio_tripadvisor_location(location_id: Optional[str] = None, geo_id: Optional[str] = None, category: Optional[Literal["restaurants", "hotels", "attractions"]] = None, url: Optional[str] = None) -> dict:
            """One TripAdvisor location in full: rating, review histogram and per-aspect sub-ratings, city ranking, price band, cuisines, amenities, address, coordinates, contact, photos, and the FIRST PAGE OF REVIEWS. Provide location_id or url. Costs 2 credits.

            Args:
                location_id: TripAdvisor location id (1-500 characters): 1899234, d1899234, or a full _Review URL. Required unless url is given.
                geo_id: Geo the location sits in; required when location_id is a bare d-id.
                category: Location family (default 'restaurants'); match the location's own type. One of: restaurants, hotels, attractions.
                url: Full tripadvisor.com _Review URL (1-500 characters), as an alternative to location_id.
            """
            _p = {"location_id": location_id, "geo_id": geo_id, "category": category, "url": url}
            return _run(lambda: client.tripadvisor.location(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tripadvisor_location)
        @function_tool
        def scavio_tripadvisor_reviews(location_id: Optional[str] = None, geo_id: Optional[str] = None, category: Optional[Literal["restaurants", "hotels", "attractions"]] = None, url: Optional[str] = None, page: Optional[int] = None) -> dict:
            """A page of TripAdvisor reviews: rating, trip date and type, reviewer home town and contribution count, management response. Page 1 already rides along in location(), so use this to page PAST it; consecutive pages can repeat one review at the boundary, so de-duplicate on review_id. Provide location_id or url. Costs 2 credits.

            Args:
                location_id: TripAdvisor location id (1-500 characters): 1899234, d1899234, or a full _Review URL. Required unless url is given.
                geo_id: Geo the location sits in; required when location_id is a bare d-id.
                category: Location family (default 'restaurants'). It sets the page size, so it must match the location's own type on any page past the first. One of: restaurants, hotels, attractions.
                url: Full tripadvisor.com _Review URL (1-500 characters), as an alternative to location_id.
                page: Reviews page, 1-based. 15 per page for restaurants, 10 for hotels and attractions; past the last page is a 404.
            """
            _p = {"location_id": location_id, "geo_id": geo_id, "category": category, "url": url, "page": page}
            return _run(lambda: client.tripadvisor.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tripadvisor_reviews)

    if all or enable_indeed:
        @function_tool
        def scavio_indeed_search(query: Optional[str] = None, location: Optional[str] = None, page: Optional[int] = None, radius: Optional[Literal[0, 5, 10, 15, 25, 35, 50, 100]] = None, max_age_days: Optional[Literal[1, 3, 7, 14]] = None, job_type: Optional[Literal["full_time", "part_time", "contract", "temporary", "internship"]] = None, min_salary: Optional[float] = None, remote: Optional[bool] = None) -> dict:
            """Indeed job postings: title, employer, rating, location, salary range, job type, benefits, posting age, apply route. 10 postings per page. Provide query or location - a location-only search (every posting in a metro) is valid. Costs 2 credits.

            Args:
                query: Job title, keywords or employer (1-500 characters). Required unless location is given.
                location: City and state, postal code, state, country, or 'Remote' (1-200 characters). Valid on its own with no query.
                page: Results page, 1-based. 10 postings per page, 1 call each.
                radius: Search radius in miles around location. Closed set: Indeed IGNORES any other value and returns the unfiltered set. Upstream default 50. One of: 0, 5, 10, 15, 25, 35, 50, 100.
                max_age_days: Maximum posting age in days. Closed set: Indeed IGNORES any other value and returns postings of every age. One of: 1, 3, 7, 14.
                job_type: Employment type filter. One of: full_time, part_time, contract, temporary, internship.
                min_salary: Minimum annual salary, >= 0. Filters on INDEED'S OWN ESTIMATE for the role, not a posted figure, so postings publishing no salary still match.
                remote: Remote postings only.
            """
            _p = {"query": query, "location": location, "page": page, "radius": radius, "max_age_days": max_age_days, "job_type": job_type, "min_salary": min_salary, "remote": remote}
            return _run(lambda: client.indeed.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_indeed_search)
        @function_tool
        def scavio_indeed_job(job_id: str) -> dict:
            """One Indeed posting in full: description text and HTML, structured salary, employment types, benefits, geocoded address, employer rating, applicant count, original ATS link. An unknown job key is a real 404 that is still billed. Costs 2 credits.

            Args:
                job_id: 16-hex Indeed job key, or any indeed.com URL carrying jk= (/viewjob, /rc/clk, /pagead/clk).
            """
            _p = {"job_id": job_id}
            return _run(lambda: client.indeed.job(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_indeed_job)
        @function_tool
        def scavio_indeed_company(company: str) -> dict:
            """Indeed employer profile: description, industry, HQ, size, revenue, CEO approval, overall and per-category ratings, reported salaries, open roles, locations. An unknown slug is a real 404 that is still billed. Costs 2 credits.

            Args:
                company: indeed.com/cmp/<slug> slug or a full profile URL (1-200 characters); slugs are untidy, e.g. 'Tata-Consultancy-Services-(tcs)'.
            """
            _p = {"company": company}
            return _run(lambda: client.indeed.company(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_indeed_company)
        @function_tool
        def scavio_indeed_company_reviews(company: str, page: Optional[int] = None) -> dict:
            """Indeed employee reviews, 20 per page, with per-category ratings, pros/cons, reviewer job title and location, plus aggregated sentiment and topic/location/job-title breakdowns. Costs 2 credits.

            Args:
                company: indeed.com/cmp/<slug> slug or a full profile URL (1-200 characters).
                page: Reviews page, 1-based. 20 reviews per page.
            """
            _p = {"company": company, "page": page}
            return _run(lambda: client.indeed.company_reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_indeed_company_reviews)

    if all or enable_airbnb:
        @function_tool
        def scavio_airbnb_search(location: str, check_in: Optional[str] = None, check_out: Optional[str] = None, adults: Optional[int] = None, children: Optional[int] = None, infants: Optional[int] = None, pets: Optional[int] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, room_type: Optional[Literal["entire_home", "private_room", "shared_room", "hotel_room"]] = None, min_bedrooms: Optional[int] = None, min_beds: Optional[int] = None, min_bathrooms: Optional[int] = None, superhost: Optional[bool] = None, instant_book: Optional[bool] = None, guest_favorite: Optional[bool] = None, free_cancellation: Optional[bool] = None, amenities: Optional[str] = None, currency: Optional[str] = None, page: Optional[int] = None, cursor: Optional[str] = None) -> dict:
            """Airbnb stays: stay-total and per-night price with the full discount ledger, rating and review count, bedrooms/beds/baths, coordinates, badges, images, dates_are_defaulted. 18 listings per page; page and cursor are mutually exclusive. Costs 1 credit.

            Args:
                location: City, region, ZIP, or a pasted airbnb.com/s/ URL (1-200 characters). An unresolvable location is a 404.
                check_in: Check-in date, YYYY-MM-DD. Must be sent with check_out; omitting both defaults to +30 days and flags dates_are_defaulted in the response.
                check_out: Check-out date, YYYY-MM-DD. Must be later than check_in; defaults to check_in plus 5 nights when omitted.
                adults: Adult guests, >= 1.
                children: Children aged 2-12, >= 0.
                infants: Infants under 2, >= 0.
                pets: Pets, >= 0.
                min_price: Minimum price for the WHOLE STAY in `currency`, not per night, >= 0. Must not exceed max_price.
                max_price: Maximum price for the WHOLE STAY in `currency`, not per night, >= 0.
                room_type: Room type. Validated before the scrape, because an unrecognised value returns the UNFILTERED set under a 200. One of: entire_home, private_room, shared_room, hotel_room.
                min_bedrooms: Minimum bedrooms, >= 0.
                min_beds: Minimum beds, >= 0.
                min_bathrooms: Minimum bathrooms, >= 0.
                superhost: Superhost listings only.
                instant_book: Instant Book listings only.
                guest_favorite: Guest Favorite listings only.
                free_cancellation: Listings with free cancellation only.
                amenities: Comma-separated amenities (1-200 characters): wifi, air_conditioning, pool, kitchen, free_parking, washer, self_check_in, tv, or raw numeric Airbnb amenity ids. An unrecognised NAME is rejected before the scrape.
                currency: ISO 4217 currency for prices, 3 letters (default 'USD'). Without it Airbnb prices off the proxy exit and identical requests disagree.
                page: Results page, 1-based. 18 listings per page. Cannot be combined with cursor.
                cursor: next_cursor from a previous response (1-500 characters); wins over page, so sending both is rejected.
            """
            _p = {"location": location, "check_in": check_in, "check_out": check_out, "adults": adults, "children": children, "infants": infants, "pets": pets, "min_price": min_price, "max_price": max_price, "room_type": room_type, "min_bedrooms": min_bedrooms, "min_beds": min_beds, "min_bathrooms": min_bathrooms, "superhost": superhost, "instant_book": instant_book, "guest_favorite": guest_favorite, "free_cancellation": free_cancellation, "amenities": amenities, "currency": currency, "page": page, "cursor": cursor}
            return _run(lambda: client.airbnb.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_airbnb_search)
        @function_tool
        def scavio_airbnb_listing(listing_id: str, check_in: Optional[str] = None, check_out: Optional[str] = None, adults: Optional[int] = None, children: Optional[int] = None, infants: Optional[int] = None, pets: Optional[int] = None, currency: Optional[str] = None) -> dict:
            """One Airbnb listing in full: description, property/room type, capacity and room counts, the complete grouped amenity list (including what the place does NOT have), host profile and stats, house rules, cancellation policy, sleeping arrangements, photo tour and the RATING BREAKDOWN. Carries NO nightly price - prices are search-only. Costs 1 credit.

            Args:
                listing_id: Airbnb listing id or a full /rooms/ URL (1-500 characters); query params are discarded, since they carry someone else's dates.
                check_in: Check-in date, YYYY-MM-DD. Must be sent with check_out. Does not produce a price: the room page has no nightly rate.
                check_out: Check-out date, YYYY-MM-DD. Must be later than check_in and sent together with it.
                adults: Adult guests, >= 1.
                children: Children aged 2-12, >= 0.
                infants: Infants under 2, >= 0.
                pets: Pets, >= 0.
                currency: ISO 4217 currency, 3 letters (default 'USD').
            """
            _p = {"listing_id": listing_id, "check_in": check_in, "check_out": check_out, "adults": adults, "children": children, "infants": infants, "pets": pets, "currency": currency}
            return _run(lambda: client.airbnb.listing(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_airbnb_listing)
        @function_tool
        def scavio_airbnb_reviews(listing_id: str, currency: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> dict:
            """Airbnb review BODIES with per-review rating, date and reviewer name/photo/location, limit/offset paged at up to 50 per call. `count` is the listing's TOTAL review count, `returned` is how many this page holds. The rating breakdown lives on listing(), not here. Costs 1 credit.

            Args:
                listing_id: Airbnb listing id or a full /rooms/ URL (1-500 characters).
                currency: ISO 4217 currency, 3 letters (default 'USD').
                limit: Reviews to return, 1-50 (default 30). Upstream returns a fixed 7 when no explicit limit is sent.
                offset: Reviews to skip before this page, >= 0 (default 0).
            """
            _p = {"listing_id": listing_id, "currency": currency, "limit": limit, "offset": offset}
            return _run(lambda: client.airbnb.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_airbnb_reviews)

    if all or enable_glassdoor:
        @function_tool
        def scavio_glassdoor_companies(query: str) -> dict:
            """START HERE. Resolve a company NAME to the employer_id every other Glassdoor method is keyed by, ranked by Glassdoor and de-duplicated. Costs 1 credit.

            Args:
                query: Company name to resolve (1-120 characters).
            """
            _p = {"query": query}
            return _run(lambda: client.glassdoor.companies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_glassdoor_companies)
        @function_tool
        def scavio_glassdoor_company(employer_id: Optional[str] = None, company: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Glassdoor employer profile: description, mission, industry, sector, HQ, size and revenue bands, stock symbol, year founded, overall and per-category ratings, star distribution, CEO approval, awards, FAQ and the five server-rendered reviews. Also returns reviews_url and salaries_url, which reviews() and salaries() accept as url to save a fetch. Provide employer_id or url. Costs 1 credit.

            Args:
                employer_id: Glassdoor employer id (1-50 characters) in any form Glassdoor writes it: '1699', 'E1699' or 'IE1699'. Must be a STRING - a JSON number is rejected.
                company: Employer name as it appears in a Glassdoor slug (1-200 characters). COSMETIC: the profile resolves on employer_id alone, it is ignored entirely when url is set, and it does not satisfy the employer_id-or-url requirement.
                url: Any glassdoor.com employer URL (1-500 characters): /Overview/, /Reviews/ or /Salary/. A non-glassdoor.com host is rejected.
            """
            _p = {"employer_id": employer_id, "company": company, "url": url}
            return _run(lambda: client.glassdoor.company(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_glassdoor_company)
        @function_tool
        def scavio_glassdoor_reviews(employer_id: Optional[str] = None, company: Optional[str] = None, url: Optional[str] = None, category: Optional[Literal["career_development", "compensation", "culture", "diversity_and_inclusion", "management", "work_life_balance"]] = None, employment_status: Optional[Literal["full_time", "part_time", "contract", "intern"]] = None) -> dict:
            """Up to THREE full Glassdoor reviews - the cap is Glassdoor's login wall - with per-axis scores, pros, cons, advice, job title, location, employment status and employer response, plus complete rating statistics, star distribution, aggregate pro/con highlight terms and per-job-title review counts. There is no page param: move the window with category and employment_status. Provide employer_id or url. Costs 1 credit.

            Args:
                employer_id: Glassdoor employer id (1-50 characters): '1699', 'E1699' or 'IE1699'. Must be a STRING - a JSON number is rejected. Addressing by id costs two upstream fetches; the customer price is unchanged.
                company: Employer name as it appears in a Glassdoor slug (1-200 characters). COSMETIC: ignored when url is set, and it does not satisfy the employer_id-or-url requirement.
                url: Any glassdoor.com employer URL (1-500 characters). Pass back reviews_url from company() to skip the resolve fetch. A non-glassdoor.com host is rejected.
                category: Restrict to reviews Glassdoor files under one topic. Closed enum: Glassdoor IGNORES an unknown value and serves the unfiltered set under a 200. Read filtered_review_count on the response to see how many match. One of: career_development, compensation, culture, diversity_and_inclusion, management, work_life_balance.
                employment_status: Restrict to one kind of employment. Closed enum for the same reason as category; FREELANCE is deliberately absent because it was never confirmed to change the result set. One of: full_time, part_time, contract, intern.
            """
            _p = {"employer_id": employer_id, "company": company, "url": url, "category": category, "employment_status": employment_status}
            return _run(lambda: client.glassdoor.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_glassdoor_reviews)
        @function_tool
        def scavio_glassdoor_salaries(employer_id: Optional[str] = None, company: Optional[str] = None, url: Optional[str] = None, page: Optional[int] = None) -> dict:
            """Glassdoor salaries by job title, 10 titles per page: base-pay and total-pay percentiles P10-P90 with medians called out, sample counts, currency, pay period and last-reported date. The figures are Glassdoor's ESTIMATES for the title, not individual reported salaries. Provide employer_id or url. Costs 1 credit.

            Args:
                employer_id: Glassdoor employer id (1-50 characters): '1699', 'E1699' or 'IE1699'. Must be a STRING - a JSON number is rejected. Addressing by id costs two upstream fetches; the customer price is unchanged.
                company: Employer name as it appears in a Glassdoor slug (1-200 characters). COSMETIC: ignored when url is set, and it does not satisfy the employer_id-or-url requirement.
                url: Any glassdoor.com employer URL (1-500 characters). Pass back salaries_url from company() to skip the resolve fetch. A non-glassdoor.com host is rejected.
                page: Results page, 1-based. Ten job titles per page; page_count on the response is how many pages exist.
            """
            _p = {"employer_id": employer_id, "company": company, "url": url, "page": page}
            return _run(lambda: client.glassdoor.salaries(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_glassdoor_salaries)

    if all or enable_yelp:
        @function_tool
        def scavio_yelp_search(term: Optional[str] = None, location: Optional[str] = None, page: Optional[int] = None, sort: Optional[Literal["recommended", "rating", "review_count"]] = None, price: Optional[list[Literal[1, 2, 3, 4]]] = None, open_now: Optional[bool] = None, attributes: Optional[list] = None, url: Optional[str] = None) -> dict:
            """Businesses in Yelp's ranked order: rating, review count, price band, categories, address, contact rails, hours, photos and a review snippet; every row carries both business_id and alias. Yelp fixes the page size at 10. Provide term and location, or url. Costs 2 credits.

            Args:
                term: What to look for (1-200 characters): a category ('plumbers'), a dish, or a business name. Required together with location unless url is given.
                location: Where to look (1-200 characters): city and region, a full address, or a postcode. Effectively required - Yelp geolocates a location-less search off the proxy exit, so the same request answers about a different metro run to run.
                page: Results page, 1-based. Yelp fixes the page size at 10.
                sort: Result ordering (upstream default 'recommended'). Closed enum: Yelp IGNORES an unrecognised sortby and serves default ranking under a 200, billing a premium scrape for a sort that never ran. One of: recommended, rating, review_count.
                price: Price bands to include, 1 ($) to 4 ($$$$); 1-4 values, combined freely - [1, 2] means $ or $$.
                open_now: Only businesses open at the moment of the request.
                attributes: Raw Yelp filter aliases, max 20, each 1-100 characters ('RestaurantsDelivery', 'GoodForKids', 'WheelchairAccessible'). A deliberate PASSTHROUGH, not an enum - Yelp's vocabulary runs to ~117 values per vertical and an alias it does not know is ignored upstream, returning unfiltered results.
                url: A full yelp.com/search URL (1-1000 characters) as an alternative to term + location; the query, offset and sort are read out of it and the URL is rebuilt.
            """
            _p = {"term": term, "location": location, "page": page, "sort": sort, "price": price, "open_now": open_now, "attributes": attributes, "url": url}
            return _run(lambda: client.yelp.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_yelp_search)
        @function_tool
        def scavio_yelp_business(business_id: Optional[str] = None, url: Optional[str] = None) -> dict:
            """One business in full: rating and per-star histogram, review count, price band, categories, address and coordinates, phone, website and menu links, hours and holidays, amenities, photos and videos, popular items, health inspections, Q&A, licences and claim status - plus the first page of reviews at no extra cost. Provide business_id or url. Costs 2 credits.

            Args:
                business_id: A Yelp business alias ('desnudo-coffee-austin-2'), its opaque encid, or any yelp.com/biz URL carrying one (1-500 characters). Search rows return both id forms.
                url: A full yelp.com/biz URL (1-1000 characters) as an alternative to business_id.
            """
            _p = {"business_id": business_id, "url": url}
            return _run(lambda: client.yelp.business(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_yelp_business)
        @function_tool
        def scavio_yelp_reviews(business_id: Optional[str] = None, url: Optional[str] = None, page: Optional[int] = None, sort: Optional[Literal["relevance", "newest", "oldest", "rating_high", "rating_low", "elites"]] = None, rating: Optional[Literal[1, 2, 3, 4, 5]] = None) -> dict:
            """A page of reviews: rating, full text, language, author profile and expertise counts, attached photos, reaction counts and owner response. 10 per page. PAGE 1 IS REDUNDANT - it re-fetches the document business() already returned - so start at page 2. Provide business_id or url. Costs 2 credits.

            Args:
                business_id: A Yelp business alias ('desnudo-coffee-austin-2'), its opaque encid, or any yelp.com/biz URL carrying one (1-500 characters).
                url: A full yelp.com/biz URL (1-1000 characters) as an alternative to business_id.
                page: Reviews page, 1-based, 10 per page. Page 1 duplicates the reviews business() already returned and costs another 2 credits - start at 2. A page past the last review is a 404, not an empty result.
                sort: Review ordering (upstream default 'relevance'). Closed enum: Yelp IGNORES an unrecognised value and serves default ranking under a billed 200. One of: relevance, newest, oldest, rating_high, rating_low, elites.
                rating: Only reviews at this star rating, 1-5. Changes filtered_review_count on the response, not review_count. One of: 1, 2, 3, 4, 5.
            """
            _p = {"business_id": business_id, "url": url, "page": page, "sort": sort, "rating": rating}
            return _run(lambda: client.yelp.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_yelp_reviews)

    if all or enable_app_store:
        @function_tool
        def scavio_app_store_search(term: str, limit: Optional[int] = None, country: Optional[str] = None, entity: Optional[Literal["software", "ipad_software", "mac_software"]] = None, lang: Optional[str] = None) -> dict:
            """Search the App Store and get up to 200 fully-shaped app rows - the same 43-field row as app() - so a search doubles as a bulk metadata fetch and as a publisher lookup. NO PAGINATION: raise limit, there is no second page. Costs 1 credit.

            Args:
                term: What to search for (1-500 characters). Apple matches an app name, a keyword OR a publisher name, so searching a developer returns their catalogue.
                limit: Apps to return, 1-200 (default 25). The ONLY lever on result volume: the search API has no pagination and every offset spelling is silently ignored.
                country: Two-letter ISO storefront code (default 'us'); decides price, currency, localised title and whether the app is sold there at all. Anything that is not exactly two letters is rejected with a free 400.
                entity: Which catalogue to search: iPhone/iPad apps ('software', the default), iPad apps, or Mac App Store apps. These are separate stores, not a filter - Mac rows carry no iPad/Apple TV screenshots, advisories, features, supported devices or Game Center flag, returning them empty rather than absent. One of: software, ipad_software, mac_software.
                lang: Listing text language as a five-letter code ('en_us', 'ja_jp'); any other shape is rejected. Independent of country: the storefront sets the price, this sets the words.
            """
            _p = {"term": term, "limit": limit, "country": country, "entity": entity, "lang": lang}
            return _run(lambda: client.app_store.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_app_store_search)
        @function_tool
        def scavio_app_store_app(app_id: str, country: Optional[str] = None) -> dict:
            """Full App Store listing: title, description, developer and seller identity, price and currency, all-time and current-version ratings, version and release notes, genres, content rating and advisories, icons at three sizes, screenshots, download size, minimum OS, languages, supported devices and the Game Center and VPP flags. Costs 1 credit.

            Args:
                app_id: App Store id - the digits after 'id' in an apps.apple.com URL - or the app's bundle id ('notion.id', 'com.burbn.instagram'); both resolve to the identical payload. 1-255 characters matching ^[A-Za-z0-9][A-Za-z0-9._-]*$, so a pasted apps.apple.com URL is rejected with a free 400. An id Apple cannot resolve is a billed 404.
                country: Two-letter ISO storefront code (default 'us'); decides price, currency, localised title and whether the app is sold there at all. Anything that is not exactly two letters is rejected with a free 400.
            """
            _p = {"app_id": app_id, "country": country}
            return _run(lambda: client.app_store.app(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_app_store_app)
        @function_tool
        def scavio_app_store_reviews(app_id: str, country: Optional[str] = None, page: Optional[int] = None, sort: Optional[Literal["most_recent", "most_helpful"]] = None) -> dict:
            """A page of App Store reviews: star rating, title, full text, author and the APP VERSION the review was written against. 50 per page, hard-stopped at page 10 - 500 reviews per storefront is Apple's anonymous ceiling. This endpoint cannot 404: an unknown id and a real app with no reviews return the same empty feed. Costs 1 credit.

            Args:
                app_id: App Store id, NUMERIC ONLY - unlike app(), the reviews feed has no bundle-id form.
                country: Two-letter ISO storefront code (default 'us'). Anything that is not exactly two letters is rejected with a free 400. Ask a different country to reach past the 500-review ceiling.
                page: Reviews page, 1-10, 50 reviews each (default 1). Apple hard-stops at page 10.
                sort: Review ordering (default 'most_recent'). The choice decides whether the vote fields mean anything: under most_recent almost every review is too new to have been voted on and returns zeroes, while most_helpful returns them densely populated.
            """
            _p = {"app_id": app_id, "country": country, "page": page, "sort": sort}
            return _run(lambda: client.app_store.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_app_store_reviews)

    if all or enable_google_play:
        @function_tool
        def scavio_google_play_search(query: str, hl: Optional[str] = None, gl: Optional[str] = None) -> dict:
            """Ranked Google Play apps: package name, title, developer, rating, install count, price and IAP range, content rating, icon and screenshots. A branded query returns the hero card as result 1 in the same row shape, plus Play's related-query rail. NO PAGINATION - one shelf of about 30 apps. Costs 2 credits.

            Args:
                query: What to search the store for (1-200 characters): an app name, a publisher, or a category phrase. Apps only - games are folded into the apps vertical, but books and films use a different card shape and are not covered.
                hl: UI language, 2-20 characters (default 'en'). Changes the STOREFRONT, not only the strings: at hl=pt-BR the title, description, install formatting and content rating all move with it. Play silently falls back to English on a value it does not serve.
                gl: Country code, 2-10 characters (default 'us'), deciding which storefront's price and availability are returned. Play silently falls back to the US storefront on a country it does not serve.
            """
            _p = {"query": query, "hl": hl, "gl": gl}
            return _run(lambda: client.google_play.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_play_search)
        @function_tool
        def scavio_google_play_app(app_id: str, hl: Optional[str] = None, gl: Optional[str] = None) -> dict:
            """Full Google Play store listing: installs including the REAL count Play publishes but never renders, rating and star histogram, description, developer identity and legal contact, price and IAPs, categories and gameplay tags, screenshots and trailer, version and Android requirement, release and update dates, changelog, the full permission tree, the Data safety table, the 20 server-rendered reviews and the similar-apps and more-by-developer rails. Costs 2 credits.

            Args:
                app_id: Android package name ('com.spotify.music') or any play.google.com URL carrying one in its id param (1-500 characters).
                hl: UI language, 2-20 characters (default 'en'). Changes the STOREFRONT, not only the strings: title, description, install formatting and content rating all move with it. Play silently falls back to English on a value it does not serve.
                gl: Country code, 2-10 characters (default 'us'), deciding which storefront's price and availability are returned. Play silently falls back to the US storefront on a country it does not serve.
            """
            _p = {"app_id": app_id, "hl": hl, "gl": gl}
            return _run(lambda: client.google_play.app(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_play_app)
        @function_tool
        def scavio_google_play_reviews(app_id: str, sort: Optional[Literal["relevance", "newest", "rating"]] = None, count: Optional[int] = None, cursor: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None) -> dict:
            """A page of Google Play reviews: star score, full text, author, thumbs-up count, developer reply and the APP VERSION the reviewer was running. Paged by cursor, up to 200 per call. app() already returns the 20 reviews Play server-renders; use this to page past them or sort differently. Costs 2 credits.

            Args:
                app_id: Android package name ('com.spotify.music') or any play.google.com URL carrying one in its id param (1-500 characters).
                sort: Review ordering (default 'newest'). Closed enum. The cursor encodes the sort, so keep this identical when paging. One of: relevance, newest, rating.
                count: Reviews to return, 1-200 (default 50); 200 is our cap, not Play's. Play honours more, but a single page that large is megabytes for one credit - page with cursor instead.
                cursor: Continuation token from a prior response's next_cursor (1-4000 characters). Opaque and SINGLE-USE, and it encodes the sort as well as the position - send it back with the SAME sort it came from. A cursor past the last review is a 404, not an empty page.
                hl: UI language, 2-20 characters (default 'en'). Changes the STOREFRONT, not only the strings. Play silently falls back to English on a value it does not serve.
                gl: Country code, 2-10 characters (default 'us'), deciding which storefront's price and availability are returned. Play silently falls back to the US storefront on a country it does not serve.
            """
            _p = {"app_id": app_id, "sort": sort, "count": count, "cursor": cursor, "hl": hl, "gl": gl}
            return _run(lambda: client.google_play.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_play_reviews)

    if all or enable_sec:
        @function_tool
        def scavio_sec_lookup(query: str, limit: Optional[int] = None, exchange: Optional[Literal["NASDAQ", "NYSE", "OTC", "CBOE"]] = None) -> dict:
            """START HERE. Resolve a company name or ticker (AAPL) to the CIK (0000320193) every other SEC EDGAR endpoint is keyed by. Up to 100 rows, tiered by match quality. Costs 1 credit.

            Args:
                query: Ticker ('AAPL', 'BRK.B'), company name, or a fragment of one (1-200 characters); each row carries its match tier as 'match'.
                limit: Rows to return, 1-100. Defaults to 10. Sizes the response; it is not a page param.
                exchange: Restrict to one listing venue; matched case-insensitively, so 'Nasdaq' also works. Filers the SEC lists with no exchange at all are excluded by any value. One of: NASDAQ, NYSE, OTC, CBOE.
            """
            _p = {"query": query, "limit": limit, "exchange": exchange}
            return _run(lambda: client.sec.lookup(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_sec_lookup)
        @function_tool
        def scavio_sec_company(cik: Optional[str] = None, ticker: Optional[str] = None) -> dict:
            """SEC filer profile: legal and former names, SIC industry, filer category, EIN, LEI, state of incorporation, fiscal year end, addresses, every ticker with its exchange, and a preview of its 10 most recent filings. Provide cik or ticker. Costs 1 credit.

            Args:
                cik: Filer CIK in any spelling (1-20 characters): 320193, 0000320193 or CIK0000320193. A ticker is accepted here too.
                ticker: Ticker symbol (1-20 characters), dotted or dashed (BRK.B / BRK-B). Wins over cik when both are given.
            """
            _p = {"cik": cik, "ticker": ticker}
            return _run(lambda: client.sec.company(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_sec_company)
        @function_tool
        def scavio_sec_filings(cik: Optional[str] = None, ticker: Optional[str] = None, form: Optional[list] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None, include_history: Optional[bool] = None) -> dict:
            """A page of one filer's filings: accession number, form and root form, filing and period dates, 8-K item codes, direct links to the primary document, filing index and attachment directory. Up to 500 per page. Provide cik or ticker. Costs 1 credit.

            Args:
                cik: Filer CIK, zero-padded or bare (1-20 characters). A ticker is accepted here too.
                ticker: Ticker symbol (1-20 characters), as an alternative to cik.
                form: Form types to keep: '10-K', ['10-K', '10-Q'] or the comma-joined '10-K,8-K'; each value 1-50 characters, at most 25 values. Matched against the form AND its root form, so 10-K also returns 10-K/A amendments; ask for '10-K/A' to get only amendments.
                date_from: Earliest filing date, inclusive (YYYY-MM-DD).
                date_to: Latest filing date, inclusive (YYYY-MM-DD).
                page: Results page, 1-based; page size is whatever limit is set to. No upper bound.
                limit: Filings per page, 1-500. Defaults to 50.
                include_history: Also fetch the archived filing history beyond EDGAR's 'recent' block, which is not a fixed window (a decade for a quiet filer, about a year for a prolific one). Off by default; at most 10 archived shards are fetched, history_truncated says when a filer had more, and it is still 1 credit.
            """
            _p = {"cik": cik, "ticker": ticker, "form": form, "date_from": date_from, "date_to": date_to, "page": page, "limit": limit, "include_history": include_history}
            return _run(lambda: client.sec.filings(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_sec_filings)
        @function_tool
        def scavio_sec_concept(concept: str, cik: Optional[str] = None, ticker: Optional[str] = None, taxonomy: Optional[str] = None, unit: Optional[str] = None, form: Optional[str] = None, limit: Optional[int] = None) -> dict:
            """Every value a filer reported for one XBRL concept, newest period first, with the form and filing each number came from. Restatements are kept, not collapsed. Up to 2000 rows. Provide cik or ticker. Costs 1 credit.

            Args:
                concept: XBRL concept tag, CASE-SENSITIVE (1-120 characters, ^[A-Za-z][A-Za-z0-9]*$): 'NetIncomeLoss' matches, 'netincomeloss' is a 404 upstream. Use facts() to list what a filer actually reports.
                cik: Filer CIK, zero-padded or bare (1-20 characters). A ticker is accepted here too.
                ticker: Ticker symbol (1-20 characters), as an alternative to cik.
                taxonomy: Reporting taxonomy (1-40 characters, ^[A-Za-z][A-Za-z0-9-]*$): us-gaap, dei, ifrs-full or srt. Defaults to 'us-gaap'.
                unit: Unit of measure to keep (1-40 characters), e.g. 'USD' vs 'USD/shares'.
                form: Form to keep (1-50 characters). EXACT match here, unlike filings(), so '10-K' excludes 10-K/A.
                limit: Rows to return, 1-2000. Defaults to 250. Sizes the response; it is not a page param.
            """
            _p = {"concept": concept, "cik": cik, "ticker": ticker, "taxonomy": taxonomy, "unit": unit, "form": form, "limit": limit}
            return _run(lambda: client.sec.concept(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_sec_concept)
        @function_tool
        def scavio_sec_facts(cik: Optional[str] = None, ticker: Optional[str] = None, taxonomy: Optional[str] = None, query: Optional[str] = None, limit: Optional[int] = None) -> dict:
            """The index of every XBRL concept a filer reports - tag, label, description, units and most recent value - across us-gaap, dei and any other taxonomy it uses. This is how you find what to ask concept() for. Up to 2000 rows. Provide cik or ticker. Costs 1 credit.

            Args:
                cik: Filer CIK, zero-padded or bare (1-20 characters). A ticker is accepted here too.
                ticker: Ticker symbol (1-20 characters), as an alternative to cik.
                taxonomy: Restrict to one taxonomy (1-40 characters), e.g. 'us-gaap' or 'dei'.
                query: Case-insensitive substring matched against the tag name and label (1-200 characters).
                limit: Rows to return, 1-2000. Defaults to 250. Sizes the response; it is not a page param.
            """
            _p = {"cik": cik, "ticker": ticker, "taxonomy": taxonomy, "query": query, "limit": limit}
            return _run(lambda: client.sec.facts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_sec_facts)
        @function_tool
        def scavio_sec_search(query: Optional[str] = None, cik: Optional[list] = None, ticker: Optional[list] = None, form: Optional[list] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, location: Optional[list] = None, sort: Optional[Literal["relevance", "newest", "oldest"]] = None, page: Optional[int] = None) -> dict:
            """EDGAR full-text search, coverage starting 2001: each hit is the matching DOCUMENT with its URL, form, filing date and filer identity, plus facets by company, form, industry and state. 100 documents per page, last page is 100. Costs 1 credit.

            Args:
                query: Full-text query over filing documents (1-500 characters); a quoted phrase is matched exactly, bare words as a bag of terms. Optional - a cik, ticker, form or date filter on its own is a valid search.
                cik: Restrict to one or more filers by CIK: a single value, a list, or a comma-joined string; each 1-20 characters, at most 25 values. Tickers are accepted here too.
                ticker: Restrict to one or more filers by ticker symbol: a single value, a list, or a comma-joined string; each 1-20 characters, at most 25 values.
                form: Form types to keep: '8-K', ['10-K', '10-Q'] or the comma-joined '10-K,10-Q'; each 1-50 characters, at most 25 values.
                date_from: Earliest filing date, inclusive (YYYY-MM-DD). Full-text coverage starts in 2001.
                date_to: Latest filing date, inclusive (YYYY-MM-DD).
                location: Filer business-address locations as EDGAR's own 2-character codes (CA, NY, and its alphanumeric codes for foreign jurisdictions): a single value, a list, or a comma-joined string; at most 25 values.
                sort: Result ordering. Defaults to the index's own relevance ranking. One of: relevance, newest, oldest.
                page: Results page, 1-based, 1-100, 100 documents per page. The SEC's index refuses a result window past 10,000, so 100 is the last page for any query.
            """
            _p = {"query": query, "cik": cik, "ticker": ticker, "form": form, "date_from": date_from, "date_to": date_to, "location": location, "sort": sort, "page": page}
            return _run(lambda: client.sec.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_sec_search)

    if all or enable_redfin:
        @function_tool
        def scavio_redfin_search(location: Optional[str] = None, region_id: Optional[int] = None, region_type: Optional[Literal[1, 2, 5, 6]] = None, listing_status: Optional[Literal["for_sale", "sold", "for_rent"]] = None, sold_within_days: Optional[int] = None, page: Optional[int] = None, limit: Optional[int] = None, sort: Optional[Literal["recommended", "price_low", "price_high", "newest", "oldest", "sqft_low", "sqft_high", "price_per_sqft_low", "price_per_sqft_high"]] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, beds_min: Optional[int] = None, beds_max: Optional[int] = None, baths_min: Optional[int] = None, sqft_min: Optional[int] = None, sqft_max: Optional[int] = None, lot_size_min: Optional[int] = None, year_built_min: Optional[int] = None, year_built_max: Optional[int] = None, max_hoa: Optional[float] = None, property_type: Optional[Literal["house", "condo", "townhouse", "multi_family", "land", "other", "co_op"]] = None, has_pool: Optional[bool] = None, max_days_on_market: Optional[int] = None, min_days_on_market: Optional[int] = None) -> dict:
            """Redfin listings: price, price per sqft, beds, baths, living area, lot size, year built, coordinates, listing remarks and full photo galleries, for sale, sold or for rent. Up to 350 per page. Provide location, or region_id together with region_type. Costs 1 credit.

            Args:
                location: A redfin.com region URL (/city/, /neighborhood/, /county/, /zipcode/) or a bare 5-digit ZIP (1-500 characters). CITY NAMES ARE NOT ACCEPTED - Redfin's own name lookup is blocked to us; use region_id + region_type instead.
                region_id: Redfin internal region id (>= 1), used together with region_type. NOT a ZIP code - the two are different number spaces and a ZIP here resolves to another city rather than failing.
                region_type: Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5 county, 6 city. Must be sent together with region_id or both are ignored in favour of location.
                listing_status: Market to search. Defaults to 'for_sale'. One of: for_sale, sold, for_rent.
                sold_within_days: Sold within the last N days (>= 1). REJECTED unless listing_status='sold', where it defaults to 90.
                page: Results page, 1-based; page size is whatever limit is set to. No upper bound.
                limit: Listings per page, 1-350. Defaults to 100.
                sort: Result sort order. Defaults to 'recommended', Redfin's own ranking. One of: recommended, price_low, price_high, newest, oldest, sqft_low, sqft_high, price_per_sqft_low, price_per_sqft_high.
                min_price: Minimum price, inclusive (>= 0). Monthly rent when listing_status='for_rent'.
                max_price: Maximum price, inclusive (>= 0). Monthly rent when listing_status='for_rent'.
                beds_min: Minimum bedrooms (whole number >= 0); fractional values are rejected.
                beds_max: Maximum bedrooms (whole number >= 0); fractional values are rejected.
                baths_min: Minimum bathrooms (whole number >= 0). WHOLE BATHS ONLY - 1.5 is rejected rather than silently truncated to 1. There is no baths_max.
                sqft_min: Minimum living area in square feet (whole number >= 0).
                sqft_max: Maximum living area in square feet (whole number >= 0).
                lot_size_min: Minimum lot size in square feet (whole number >= 0). There is no lot_size_max.
                year_built_min: Earliest year built (whole number >= 0).
                year_built_max: Latest year built (whole number >= 0).
                max_hoa: Maximum monthly HOA fee in dollars (>= 0).
                property_type: Restrict to one property type. One of: house, condo, townhouse, multi_family, land, other, co_op.
                has_pool: Only listings with a pool.
                max_days_on_market: Listed at most N days ago (whole number >= 0). Cannot be combined with min_days_on_market - Redfin expresses both bounds through one param.
                min_days_on_market: Listed at least N days ago (whole number >= 0). Cannot be combined with max_days_on_market.
            """
            _p = {"location": location, "region_id": region_id, "region_type": region_type, "listing_status": listing_status, "sold_within_days": sold_within_days, "page": page, "limit": limit, "sort": sort, "min_price": min_price, "max_price": max_price, "beds_min": beds_min, "beds_max": beds_max, "baths_min": baths_min, "sqft_min": sqft_min, "sqft_max": sqft_max, "lot_size_min": lot_size_min, "year_built_min": year_built_min, "year_built_max": year_built_max, "max_hoa": max_hoa, "property_type": property_type, "has_pool": has_pool, "max_days_on_market": max_days_on_market, "min_days_on_market": min_days_on_market}
            return _run(lambda: client.redfin.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_redfin_search)
        @function_tool
        def scavio_redfin_property(property_id: str) -> dict:
            """One Redfin listing in full: price, Redfin Estimate and rental estimate, complete MLS fact sheet, price and tax history, listing agents, open houses, schools, climate risk, walkability, sun exposure, monthly weather, permits, zoning, comparable sales and photos. Costs 1 credit.

            Args:
                property_id: Redfin property id, or any redfin.com listing URL carrying one (1-500 characters).
            """
            _p = {"property_id": property_id}
            return _run(lambda: client.redfin.property(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_redfin_property)
        @function_tool
        def scavio_redfin_market(location: Optional[str] = None, region_id: Optional[int] = None, region_type: Optional[Literal[1, 2, 5, 6]] = None) -> dict:
            """Redfin housing-market stats for a region: median list and sale price, price per sqft, sale-to-list ratio, average offers and days on market, YoY movement, 0-100 compete score, live inventory by property type and by bedroom count, and Redfin agent presence. Provide location, or region_id together with region_type. Costs 1 credit.

            Args:
                location: A redfin.com region URL (/city/, /neighborhood/, /county/, /zipcode/) or a bare 5-digit ZIP (1-500 characters). City names are not accepted.
                region_id: Redfin internal region id (>= 1), used together with region_type. Not a ZIP code.
                region_type: Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5 county, 6 city. Must be sent together with region_id or both are ignored in favour of location.
            """
            _p = {"location": location, "region_id": region_id, "region_type": region_type}
            return _run(lambda: client.redfin.market(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_redfin_market)

    if all or enable_companies_house:
        @function_tool
        def scavio_companies_house_search(query: str, page: Optional[int] = None) -> dict:
            """START HERE. Search the UK register by name and get the company_number every other Companies House endpoint is keyed by, plus status, incorporation or dissolution date, registered office and matched former names. 20 per page, last page is 50. Costs 1 credit.

            Args:
                query: Company name or fragment (1-200 characters, non-blank). Matches CURRENT AND FORMER names.
                page: Results page, 1-based, 1-50, 20 results per page. Defaults to 1. The register serves only a 1000-result window per term whatever hit count it prints, and answers page 51 with HTTP 416.
            """
            _p = {"query": query, "page": page}
            return _run(lambda: client.companies_house.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_companies_house_search)
        @function_tool
        def scavio_companies_house_company(company_number: str) -> dict:
            """Full UK register entry: status, type, incorporation and dissolution dates, registered office, SIC codes, previous names, accounts and confirmation-statement due dates with overdue flags, and whether it has charges, insolvency history, officers or UK establishments. Costs 1 credit.

            Args:
                company_number: UK company number (1-20 characters), zero-padded and upper-cased for you, so '445790' and 'sc090312' both work. Registry prefixes supported: SC, NI, OC, SO, NC, FC, BR, CE.
            """
            _p = {"company_number": company_number}
            return _run(lambda: client.companies_house.company(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_companies_house_company)
        @function_tool
        def scavio_companies_house_officers(company_number: str, page: Optional[int] = None) -> dict:
            """UK company officers, current and resigned, 35 per page: name, role, appointment and resignation dates, correspondence address, nationality, country of residence, month-and-year date of birth and identity-verification status. Costs 1 credit.

            Args:
                company_number: UK company number (1-20 characters), zero-padded and upper-cased for you.
                page: Results page, 1-based, 35 per page. Defaults to 1. No upper bound: past the last page the register answers an ordinary 200 with an empty list, identical to a company with no officers.
            """
            _p = {"company_number": company_number, "page": page}
            return _run(lambda: client.companies_house.officers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_companies_house_officers)
        @function_tool
        def scavio_companies_house_filing_history(company_number: str, page: Optional[int] = None) -> dict:
            """UK filings, most recent first: date, filing type code (AA, CS01, SH03), description, register annotations and child documents, and a link to the filed PDF with its page count. A filing the register has not finished processing carries a processing_note instead of a document. Costs 1 credit.

            Args:
                company_number: UK company number (1-20 characters), zero-padded and upper-cased for you.
                page: Results page, 1-based. Defaults to 1. No upper bound: past the last page the register answers an ordinary 200 with an empty list.
            """
            _p = {"company_number": company_number, "page": page}
            return _run(lambda: client.companies_house.filing_history(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_companies_house_filing_history)

    if all or enable_g2:
        @function_tool
        def scavio_g2_search(query: Optional[str] = None, page: Optional[int] = None, limit: Optional[int] = None, sort: Optional[Literal["relevance", "popular", "alphabetical", "rating"]] = None, rating: Optional[Literal[1, 2, 3, 4, 5]] = None, url: Optional[str] = None) -> dict:
            """Search G2, the B2B software review site, for products: star rating, review count, vendor, categories, seller description and logo, with product_id and slug on every row. Up to 100 results per page (server default 20) and page-paginated; total_results is G2's Products-tab headline and caps at 10000, while total_by_type splits the query across products, sellers, categories and discussions. Provide query or url. Costs 5 credits.

            Args:
                query: Search term (1-200 characters). Provide this or url.
                page: 1-based page number; page size follows limit (server default 20). G2 keeps paginating well past its own widget's page links.
                limit: Results per page (1-100; server default 20). The 100 ceiling is ours, to keep a single request inside the 60s deadline; G2 itself paginates at any size.
                sort: Result sort order (server default 'relevance'). Closed enum: G2 silently accepts an unknown sort and answers 200 with an unstated ordering. One of: relevance, popular, alphabetical, rating.
                rating: Only products at or above this star rating (1-5, sent as an integer). Omit for no rating floor. One of: 1, 2, 3, 4, 5.
                url: Full g2.com/search URL, as an alternative to query (1-1000 characters; the host is checked by the transport).
            """
            _p = {"query": query, "page": page, "limit": limit, "sort": sort, "rating": rating, "url": url}
            return _run(lambda: client.g2.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_g2_search)
        @function_tool
        def scavio_g2_product(product_id: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Full G2 product profile: rating with per-star histogram, review count, vendor, description and seller website, pricing editions with parsed amounts, feature groups, categories and breadcrumbs, supported languages, integrations, alternatives, head-to-head comparisons, media, community discussions and G2's AI-derived pros and cons. Carries NO review text at all -- G2 loads review bodies in a separate frame, so call reviews() for those. Provide product_id or url. Costs 5 credits.

            Args:
                product_id: G2 product slug ('notion') or the numeric G2 id ('82623') as a string (1-200 characters); both resolve on the same upstream path.
                url: Full g2.com product URL, as an alternative to product_id (1-1000 characters).
            """
            _p = {"product_id": product_id, "url": url}
            return _run(lambda: client.g2.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_g2_product)
        @function_tool
        def scavio_g2_reviews(product_id: Optional[str] = None, url: Optional[str] = None, page: Optional[int] = None, sort: Optional[Literal["relevance", "newest", "most_helpful", "rating_high", "rating_low"]] = None, rating: Optional[Literal[1, 2, 3, 4, 5]] = None, company_size: Optional[Literal["small_business", "mid_market", "enterprise"]] = None, role: Optional[Literal["user", "administrator", "executive_sponsor", "internal_consultant", "consultant", "agency", "industry_analyst"]] = None, region: Optional[Literal["north_america", "europe", "asia", "latin_america", "anz", "middle_east", "africa"]] = None, query: Optional[str] = None) -> dict:
            """A page of G2 reviews: rating, title, likes and dislikes, problems solved, reviewer job title, industry and company size, validated and incentivized flags -- plus what the profile page has no form of: exact per-star counts, pros and cons with per-theme counts, and company-size, role, industry, region and category facets with counts. Fixed at 10 reviews per page and paginates well past the 10 pages G2's own widget links to. Provide product_id or url. Costs 5 credits.

            Args:
                product_id: G2 product slug or numeric G2 id as a string (1-200 characters).
                url: Full g2.com reviews URL, as an alternative to product_id (1-1000 characters).
                page: 1-based page number; fixed at 10 reviews per page.
                sort: Review sort order (server default 'relevance'). Closed enum: an unknown sort is silently accepted upstream and never runs. One of: relevance, newest, most_helpful, rating_high, rating_low.
                rating: Only reviews in this star bucket (1-5, sent as an integer). Buckets are half- star-inclusive: 1 returns 0, 0.5 and 1-star reviews. One of: 1, 2, 3, 4, 5.
                company_size: Reviewer company size: small_business is 50 employees or fewer, mid_market 51-1000, enterprise over 1000. Closed enum -- an unknown value matches nothing and returns a billed 'Reviews (0)'.
                role: Reviewer role. Closed enum -- an unknown value matches nothing rather than erroring. One of: user, administrator, executive_sponsor, internal_consultant, consultant, agency, industry_analyst.
                region: Reviewer region. Closed enum -- an unknown value matches nothing rather than erroring. One of: north_america, europe, asia, latin_america, anz, middle_east, africa.
                query: Full-text search within this product's reviews (1-200 characters); narrows the review list AND every facet count.
            """
            _p = {"product_id": product_id, "url": url, "page": page, "sort": sort, "rating": rating, "company_size": company_size, "role": role, "region": region, "query": query}
            return _run(lambda: client.g2.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_g2_reviews)

    if all or enable_capterra:
        @function_tool
        def scavio_capterra_search(query: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Search Capterra, the B2B software review site: 20 ranked products with name, vendor description, rating, review count, logo and paid-placement flag, each row carrying product_id and slug. The result set is fixed at 20 and does NOT paginate -- Capterra serves identical rows for page 2, so there is deliberately no page parameter. Provide query or url. Costs 2 credits.

            Args:
                query: Search term (1-200 characters). Required in practice: a term-less Capterra search serves a fixed popular-products list unrelated to the caller.
                url: Full capterra.com search URL, as an alternative to query (1-1000 characters; the transport also accepts capterra.co.uk and capterra.com.br hosts).
            """
            _p = {"query": query, "url": url}
            return _run(lambda: client.capterra.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_capterra_search)
        @function_tool
        def scavio_capterra_product(product_id: Optional[str] = None, slug: Optional[str] = None, url: Optional[str] = None) -> dict:
            """Full Capterra profile: rating with per-star histogram and the four scored criteria, likelihood to recommend, review sentiment and topics, the complete pricing table with every plan and its features, every rated feature and integration, AI-derived pros and cons with the quoted review, FAQs, screenshots, badges and awards, competitor comparisons and alternatives, and the buyer profile by company size, industry and job function -- PLUS the 25 most recent reviews at no extra cost. vendor is always null here: Capterra does not publish it as structured data on the product page. Provide product_id or url. Costs 2 credits.

            Args:
                product_id: The number in a Capterra product path such as /p/186596/Notion/ (1-50 characters). Must be a STRING -- a JSON number is rejected.
                slug: Product slug (1-200 characters). Cosmetic on this endpoint -- a wrong slug still returns the right profile -- but load-bearing on reviews().
                url: Full Capterra product URL, as an alternative to product_id (1-1000 characters).
            """
            _p = {"product_id": product_id, "slug": slug, "url": url}
            return _run(lambda: client.capterra.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_capterra_product)
        @function_tool
        def scavio_capterra_reviews(product_id: Optional[str] = None, slug: Optional[str] = None, url: Optional[str] = None, page: Optional[int] = None) -> dict:
            """A page of Capterra reviews: overall score plus five per-criterion scores, title, pros, cons, advice, usage duration, incentivized flag, alternatives considered and what they switched from, reviewer job title, industry and company size, and the vendor response -- plus a competitor list richer than the profile's, each alternative with its own rating histogram and starting price. 25 reviews per page, capped at page 100. Page 1 already rides along inside product(), so use this to page past it. Provide product_id or url. Costs 2 credits.

            Args:
                product_id: Capterra product id as a string (1-50 characters).
                slug: Product slug (1-200 characters). LOAD-BEARING here: it is case-sensitive upstream and a wrong one silently serves page one under a billed 200. Pass back the slug from search() or product().
                url: Full Capterra reviews URL, as an alternative to product_id (1-1000 characters). Passing back reviews_url from product() is the reliable way to page.
                page: 1-based page number (1-100); 25 reviews per page. 100 is a hard cap whatever the review count says -- past it Capterra answers 200 with page one.
            """
            _p = {"product_id": product_id, "slug": slug, "url": url, "page": page}
            return _run(lambda: client.capterra.reviews(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_capterra_reviews)

    if all or enable_google_ads:
        @function_tool
        def scavio_google_ads_advertisers(query: str, region: Optional[str] = None, limit: Optional[int] = None) -> dict:
            """Resolve a brand name or domain to the advertiser_id that search() and creative() are keyed by. Returns two row kinds in one list: 'advertiser' rows carrying the id, verified name, verification country and total ad count as a range, and 'domain' rows carrying a website. A name query returns both kinds; a domain-shaped query returns domains only. Autocomplete-backed, roughly 20 rows per arm, and it does not paginate. Costs 1 credit.

            Args:
                query: Brand name or domain to resolve (1-200 characters).
                region: ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo criteria id as a string (2-12 characters). Default: no region filter.
                limit: Rows per arm (1-20; server default 10). Advertisers and domains are capped separately, so a name query can return up to twice this many rows.
            """
            _p = {"query": query, "region": region, "limit": limit}
            return _run(lambda: client.google_ads.advertisers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_ads_advertisers)
        @function_tool
        def scavio_google_ads_search(domain: Optional[str] = None, advertiser_id: Optional[str] = None, region: Optional[str] = None, format: Optional[Literal["text", "image", "video"]] = None, platform: Optional[Literal["play", "maps", "search", "shopping", "youtube"]] = None, topic: Optional[Literal["all", "political"]] = None, limit: Optional[int] = None, cursor: Optional[str] = None) -> dict:
            """Every ad Google Ads Transparency holds for one advertiser: the creative (archived image, rich-media bundle, Google's renderer link, dimensions), advertiser id and name, format, first and last seen dates and days actually run, plus total_ads_min and total_ads_max -- Google publishes the advertiser's ad total as a range, never an exact figure. Up to 100 ads per page (server default 40); paginate by sending next_cursor back as cursor alongside the SAME filters. Provide domain or advertiser_id. Costs 1 credit.

            Args:
                domain: Advertiser website (1-253 characters): bare host, www host or full URL, reduced to the registrable host. The only way to get `domain` back on each row.
                advertiser_id: Google advertiser id, e.g. 'AR16735076323512287233' (3-40 characters). The shape is checked before any request, so a typo costs no credits. Querying by id drops `domain` from every row.
                region: ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo criteria id as a string (2-12 characters). Scopes the deep links on every row, and the same advertiser can share zero creatives between two countries. Default: worldwide.
                format: Creative format. The three sets are disjoint -- an advertiser's text, image and video ads share no creatives. Default: all formats.
                platform: Google surface the ad ran on. Default: all surfaces. One of: play, maps, search, shopping, youtube.
                topic: Ad topic (server default 'all'). One of: all, political.
                limit: Ads per page (1-100; server default 40). 100 is a hard upstream ceiling, not our policy: Google answers a larger request with zero rows rather than an error.
                cursor: next_cursor from the previous response (1-4000 characters), 100 ads per page. Re-send the same filters alongside it; next_cursor is null once exhausted.
            """
            _p = {"domain": domain, "advertiser_id": advertiser_id, "region": region, "format": format, "platform": platform, "topic": topic, "limit": limit, "cursor": cursor}
            return _run(lambda: client.google_ads.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_ads_search)
        @function_tool
        def scavio_google_ads_creative(advertiser_id: str, creative_id: str) -> dict:
            """One creative in full, and the only endpoint carrying its history: every size variation of the asset, the impression bucket, the per-region breakdown with first and last shown dates and a per-surface impression split inside each region, the format, Google's category label and the funder disclosure on political ads. Impressions and first_shown are EEA-only (DSA-compelled) and come back null for US creatives, and an impression bucket may carry only a lower or only an upper bound. Costs 1 credit.

            Args:
                advertiser_id: Google advertiser id, e.g. 'AR16735076323512287233' (3-40 characters).
                creative_id: Creative id (3-40 characters). It must belong to the advertiser_id sent with it -- the lookup is keyed by the pair and a mismatched pair is a 404.
            """
            _p = {"advertiser_id": advertiser_id, "creative_id": creative_id}
            return _run(lambda: client.google_ads.creative(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_ads_creative)

    if all or enable_meta_ads:
        @function_tool
        def scavio_meta_ads_search(query: str, country: Optional[str] = None, active_status: Optional[Literal["all", "active", "inactive"]] = None, ad_type: Optional[Literal["all", "political_and_issue_ads"]] = None, media_type: Optional[Literal["all", "image", "video", "meme", "image_and_meme", "none"]] = None, search_type: Optional[Literal["keyword_unordered", "keyword_exact_phrase"]] = None, cursor: Optional[str] = None) -> dict:
            """Search the Meta Ad Library by keyword: 30 ads on page 1 with the full creative -- page name, ad copy, headline, CTA, images and videos, the platforms each ran on and its run dates -- then 10 ads per cursor page, walking has_next_page to the end of the query. total_results caps at 50000 with total_is_capped true, because Meta only reports '>50,000'; never present it as an exact count. Every page costs 1 credit.

            Args:
                query: Keyword to search the ad library for (1-200 characters).
                country: Ad library country as an exactly 2-character ISO 3166-1 alpha-2 code (server default 'US').
                active_status: Whether the ad is still running (server default 'all'). One of: all, active, inactive.
                ad_type: Set 'political_and_issue_ads' to expose spend, reach, impressions and the paid-for-by disclosure; commercial ads leave all four null (server default 'all').
                media_type: Creative media filter. Default: no media filter. One of: all, image, video, meme, image_and_meme, none.
                search_type: How the query is matched (server default 'keyword_unordered'). One of: keyword_unordered, keyword_exact_phrase.
                cursor: next_cursor from the previous response: page 1 is 30 ads, every cursor page is 10. The cursor is a self-contained blob, so ALL other filters are ignored when it is present.
            """
            _p = {"query": query, "country": country, "active_status": active_status, "ad_type": ad_type, "media_type": media_type, "search_type": search_type, "cursor": cursor}
            return _run(lambda: client.meta_ads.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_meta_ads_search)
        @function_tool
        def scavio_meta_ads_advertiser(page_id: str, country: Optional[str] = None, active_status: Optional[Literal["all", "active", "inactive"]] = None, ad_type: Optional[Literal["all", "political_and_issue_ads"]] = None, media_type: Optional[Literal["all", "image", "video", "meme", "image_and_meme", "none"]] = None, cursor: Optional[str] = None) -> dict:
            """Every ad a Facebook Page is running, by numeric page id: 30 ads on page 1 with the same creative detail as search(), then 10 ads per cursor page, walking has_next_page to the end of the advertiser. Every page costs 1 credit.

            Args:
                page_id: The advertiser's numeric Facebook Page id (3-25 digits, as a string).
                country: Ad library country as an exactly 2-character ISO 3166-1 alpha-2 code (server default 'US').
                active_status: Whether the ad is still running (server default 'all'). One of: all, active, inactive.
                ad_type: Set 'political_and_issue_ads' to expose spend, reach, impressions and the paid-for-by disclosure; commercial ads leave all four null (server default 'all').
                media_type: Creative media filter. Default: no media filter. One of: all, image, video, meme, image_and_meme, none.
                cursor: next_cursor from the previous response: page 1 is 30 ads, every cursor page is 10. ALL other filters are ignored when it is present.
            """
            _p = {"page_id": page_id, "country": country, "active_status": active_status, "ad_type": ad_type, "media_type": media_type, "cursor": cursor}
            return _run(lambda: client.meta_ads.advertiser(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_meta_ads_advertiser)
        @function_tool
        def scavio_meta_ads_ad(ad_archive_id: str) -> dict:
            """One Meta ad in full by archive id: creative, advertiser, run dates, the platforms it ran on, and the political disclosure when the ad carries one. Commercial ads leave spend, reach and impressions null. Costs 1 credit.

            Args:
                ad_archive_id: Meta ad archive id (3-25 digits, as a string).
            """
            _p = {"ad_archive_id": ad_archive_id}
            return _run(lambda: client.meta_ads.ad(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_meta_ads_ad)

    if all or enable_extract:
        @function_tool
        def scavio_extract(url: str, format: Optional[Literal["html", "markdown", "text"]] = None, mode: Optional[Literal["normal", "advanced", "ultra"]] = None) -> dict:
            """Read any URL and get the page back as raw HTML, readability Markdown or plain text: { url, format, mode, content, content_length }. Tier-priced by mode -- normal and advanced cost 1 credit, ultra costs 2 -- and only a successful extraction is billed, so a dead link, bot wall or timeout costs nothing.

            Args:
                url: Page to read (1-2048 characters). http(s) only; a bare host is upgraded to https, and loopback, private, link-local and metadata hosts are rejected with a 400.
                format: Output format: 'html' is the raw page, 'markdown' a readability extraction, 'text' that markdown flattened to plain text (server default 'markdown').
                mode: Fetch tier, and the price-bearing parameter: 'normal' plain datacenter fetch (1 credit), 'advanced' full browser render (1 credit), 'ultra' the hardest-target tier (2 credits). Server default 'normal'.
            """
            _p = {"url": url, "format": format, "mode": mode}
            return _run(lambda: client.extract(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_extract)
    return tools
