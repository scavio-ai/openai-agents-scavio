"""Scavio tools for the OpenAI Agents SDK.

Build the tools with `get_scavio_tools()` and pass them to an Agent:

    from agents import Agent
    from openai_agents_scavio import get_scavio_tools

    agent = Agent(name="Search", tools=get_scavio_tools())

Covers the whole Scavio API: Google, YouTube, Amazon, Walmart, Reddit, TikTok,
TikTok Shop, Instagram, X and LinkedIn. 97 tools over the 98 live billable
endpoints - /youtube/metadata is a deprecated alias of /youtube/video and is not
registered twice.

Each provider is gated by an ``enable_*`` flag. Tools return the Scavio JSON response.
"""

import os
from typing import Any, Callable, Dict, Optional

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
    all: bool = False,
) -> list:
    """Build Scavio function tools for an OpenAI Agents SDK Agent.

    Args:
        api_key: Scavio API key. Falls back to the SCAVIO_API_KEY env var.
        enable_google: Register the Google tools (14). Defaults to True.
        enable_amazon: Register the Amazon tools (3). Defaults to True.
        enable_walmart: Register the Walmart tools (2). Defaults to True.
        enable_youtube: Register the YouTube tools (15). Defaults to True.
        enable_reddit: Register the Reddit tools (12). Defaults to True.
        enable_tiktok: Register the TikTok tools (11). Defaults to True.
        enable_tiktok_shop: Register the TikTok Shop tools (8). Defaults to True.
        enable_instagram: Register the Instagram tools (12). Defaults to True.
        enable_x: Register the X tools (11). Defaults to True.
        enable_linkedin: Register the LinkedIn tools (9). Defaults to True.
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
        def scavio_google_search(query: str, device: Optional[str] = None, start: Optional[int] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None, lr: Optional[str] = None, cr: Optional[str] = None, safe: Optional[str] = None, nfpr: Optional[bool] = None, filter: Optional[str] = None, time_period: Optional[str] = None, resolve_ai_overview: Optional[bool] = None, include_html: Optional[bool] = None) -> dict:
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
        def scavio_google_ai_mode(query: str, device: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None, safe: Optional[str] = None, include_html: Optional[bool] = None) -> dict:
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
        def scavio_google_maps_reviews(data_id: Optional[str] = None, place_id: Optional[str] = None, num: Optional[int] = None, next_page_token: Optional[str] = None, sort_by: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None) -> dict:
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
        def scavio_google_shopping(query: str, device: Optional[str] = None, start: Optional[int] = None, min_price: Optional[int] = None, max_price: Optional[int] = None, sort_by: Optional[int] = None, free_shipping: Optional[bool] = None, on_sale: Optional[bool] = None, shoprs: Optional[str] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None) -> dict:
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
        def scavio_google_shopping_product(catalog_id: Optional[str] = None, query: Optional[str] = None, immersive_product_page_token: Optional[str] = None, page_token: Optional[str] = None, product_id: Optional[str] = None, device: Optional[str] = None, sort_by: Optional[str] = None, load_all_stores: Optional[bool] = None, more_stores: Optional[bool] = None, hl: Optional[str] = None, gl: Optional[str] = None, google_domain: Optional[str] = None, location: Optional[str] = None, uule: Optional[str] = None) -> dict:
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
        def scavio_google_trends(query: str, geo: Optional[str] = None, hl: Optional[str] = None, date: Optional[str] = None, tz: Optional[str] = None, data_type: Optional[str] = None, cat: Optional[str] = None, gprop: Optional[str] = None, region: Optional[str] = None) -> dict:
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
        def scavio_google_trending(geo: str, hl: Optional[str] = None, hours: Optional[int] = None, cat: Optional[int] = None, sort: Optional[str] = None, status: Optional[str] = None) -> dict:
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

    if all or enable_walmart:
        @function_tool
        def scavio_walmart_search(query: str, domain: Optional[str] = None, device: Optional[str] = None, sort_by: Optional[str] = None, start_page: Optional[int] = None, min_price: Optional[int] = None, max_price: Optional[int] = None, fulfillment_speed: Optional[str] = None, fulfillment_type: Optional[str] = None, delivery_zip: Optional[str] = None, store_id: Optional[str] = None) -> dict:
            """Search Walmart for products matching a query. Costs 1 credit.

            Args:
                query: The product search query.
                domain: Walmart domain.
                device: Device profile: desktop, mobile or tablet.
                sort_by: Sort order: best_match, price_low, price_high, best_seller.
                start_page: First page to return (1-indexed).
                min_price: Minimum price filter (USD).
                max_price: Maximum price filter (USD).
                fulfillment_speed: Delivery speed: today, tomorrow, 2_days, anytime.
                fulfillment_type: Fulfillment type filter; in_store is the only value.
                delivery_zip: Delivery ZIP/postal code.
                store_id: Restrict to a store id.
            """
            _p = {"query": query, "domain": domain, "device": device, "sort_by": sort_by, "start_page": start_page, "min_price": min_price, "max_price": max_price, "fulfillment_speed": fulfillment_speed, "fulfillment_type": fulfillment_type, "delivery_zip": delivery_zip, "store_id": store_id}
            return _run(lambda: client.walmart.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_search)
        @function_tool
        def scavio_walmart_product(product_id: str, domain: Optional[str] = None, device: Optional[str] = None, delivery_zip: Optional[str] = None, store_id: Optional[str] = None) -> dict:
            """Fetch full Walmart product details by product id. Costs 1 credit.

            Args:
                product_id: Walmart product id.
                domain: Walmart domain.
                device: Device profile: desktop, mobile or tablet.
                delivery_zip: Delivery ZIP/postal code.
                store_id: Restrict to a store id.
            """
            _p = {"product_id": product_id, "domain": domain, "device": device, "delivery_zip": delivery_zip, "store_id": store_id}
            return _run(lambda: client.walmart.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_product)

    if all or enable_youtube:
        @function_tool
        def scavio_youtube_search(query: str, upload_date: Optional[str] = None, type: Optional[str] = None, duration: Optional[str] = None, sort_by: Optional[str] = None, features: Optional[list] = None, cursor: Optional[str] = None, hd: Optional[bool] = None, subtitles: Optional[bool] = None, creative_commons: Optional[bool] = None, live: Optional[bool] = None) -> dict:
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
        def scavio_youtube_shorts(query: str, sort_by: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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
        def scavio_youtube_transcript(video_id: str, language: Optional[str] = None, format: Optional[str] = None) -> dict:
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
        def scavio_reddit_post_comments(post_id: str, sort: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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
        def scavio_reddit_comment_replies(post_id: str, cursor: str, sort: Optional[str] = None) -> dict:
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
        def scavio_reddit_subreddit_posts(subreddit: str, sort: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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
        def scavio_reddit_user_posts(username: str, sort: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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
        def scavio_reddit_user_comments(username: str, sort: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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
        def scavio_tiktok_user_posts(sec_user_id: str, cursor: Optional[str] = None, count: Optional[int] = None, sort_type: Optional[str] = None) -> dict:
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
        def scavio_tiktok_search_videos(keyword: str, cursor: Optional[str] = None, count: Optional[int] = None, sort_type: Optional[str] = None, publish_time: Optional[str] = None) -> dict:
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
        def scavio_tiktok_shop_search_suggestions(search: str, region: Optional[str] = None) -> dict:
            """Fetch TikTok Shop keyword autocomplete and expansion for a partial query. Costs 1 credit. Suggestions are not guaranteed prefix matches: a misspelling returns typo corrections, and results can include brand and shop names.

            Args:
                search: Partial search keyword (1-100 characters).
                region: Marketplace region: US (default), GB, SG, MY, PH, TH, VN, ID.
            """
            _p = {"search": search, "region": region}
            return _run(lambda: client.tiktok_shop.search_suggestions(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_search_suggestions)
        @function_tool
        def scavio_tiktok_shop_product(product_id: str, region: Optional[str] = None) -> dict:
            """Fetch full TikTok Shop product detail: description, images, variants with stock, shipping, shop profile, category path and top reviews. Costs 1 credit. Two hard limits: it returns NO price (upstream masks it, so read prices from scavio_tiktok_shop_search, scavio_tiktok_shop_shop_products or scavio_tiktok_shop_category_products), and only about 44% of search product ids resolve here. A 404 is a normal outcome, not a transient error: skip that product instead of retrying, and try scavio_tiktok_shop_product_reviews, which often works for ids this cannot resolve.

            Args:
                product_id: TikTok Shop product id (6-25 digits).
                region: Marketplace region: US (default), GB, SG, MY, PH, TH, VN, ID.
            """
            _p = {"product_id": product_id, "region": region}
            return _run(lambda: client.tiktok_shop.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_shop_product)
        @function_tool
        def scavio_tiktok_shop_product_reviews(product_id: str, page: Optional[int] = None, page_size: Optional[int] = None, sort: Optional[str] = None, rating: Optional[int] = None, has_media: Optional[bool] = None, verified_only: Optional[bool] = None, region: Optional[str] = None) -> dict:
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
        def scavio_tiktok_shop_category_products(category_id: str, cursor: Optional[str] = None, region: Optional[str] = None) -> dict:
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
        def scavio_tiktok_shop_shop_products(shop_id: str, cursor: Optional[str] = None, region: Optional[str] = None) -> dict:
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
        def scavio_instagram_post_comments(shortcode: Optional[str] = None, url: Optional[str] = None, cursor: Optional[str] = None, sort_order: Optional[str] = None) -> dict:
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
        def scavio_x_search(search: str, search_type: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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
        def scavio_x_tweet_comments(tweet_id: str, rank: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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
        def scavio_linkedin_person_posts(username: Optional[str] = None, url: Optional[str] = None, type: Optional[str] = None, cursor: Optional[str] = None) -> dict:
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

    return tools
