"""Scavio tools for the OpenAI Agents SDK.

Build the tools with `get_scavio_tools()` and pass them to an Agent:

    from agents import Agent
    from openai_agents_scavio import get_scavio_tools

    agent = Agent(name="Search", tools=get_scavio_tools())

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
    enable_instagram: bool = True,
    all: bool = False,
) -> list:
    """Build Scavio function tools for an OpenAI Agents SDK Agent.

    Args:
        api_key: Scavio API key. Falls back to the SCAVIO_API_KEY env var.
        enable_google: Register the Google tools. Defaults to True.
        enable_amazon: Register the Amazon tools. Defaults to True.
        enable_walmart: Register the Walmart tools. Defaults to True.
        enable_youtube: Register the Youtube tools. Defaults to True.
        enable_reddit: Register the Reddit tools. Defaults to True.
        enable_tiktok: Register the Tiktok tools. Defaults to True.
        enable_instagram: Register the Instagram tools. Defaults to True.
        all: Register every tool, ignoring the individual flags.
    """
    client = ScavioClient(api_key=api_key or os.getenv("SCAVIO_API_KEY"))
    tools: list = []

    if all or enable_google:
        @function_tool
        def scavio_google_search(query: str, country_code: Optional[str] = None, language: Optional[str] = None, page: Optional[int] = None, device: Optional[str] = None, nfpr: Optional[bool] = None) -> dict:
            """Search Google for real-time web results (organic results, ads, and the AI Overview when present). Costs 1 credit.

            Args:
                query: The search query.
                country_code: Two-letter country of the search, e.g. us.
                language: Two-letter UI language code, e.g. en.
                page: Result page number (1-based).
                device: Device profile: desktop or mobile.
                nfpr: Disable query auto-correction when true.
            """
            _p = {"query": query, "gl": country_code, "hl": language, "device": device, "nfpr": nfpr}
            if page is not None and page > 1:
                _p["start"] = (page - 1) * 10
            return _run(lambda: client.google.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_google_search)

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
            """Search Amazon for products matching a query. Results are unsorted and cannot be filtered.

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
            """Fetch full Amazon product details by ASIN. price is the buy-box price only.

            Args:
                asin: Amazon Standard Identification Number (ASIN).
                country: Marketplace country code (ISO 3166-1 alpha-2), not a domain: us (default), gb (the UK is gb, not uk), ca, de, fr, es, it, jp, in, au, br, mx, nl, pl, se, sg, ae, sa, eg, cn, be, tr. An unknown code falls back to us.
            """
            _p = {"asin": asin, "country": country}
            return _run(lambda: client.amazon.product(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_amazon_product)
        @function_tool
        def scavio_amazon_offers(asin: str, country: Optional[str] = None) -> dict:
            """List every seller offer for an Amazon ASIN: price, seller, condition, shipping, buy box. Page 1 only.

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
            """Search Walmart for products matching a query.

            Args:
                query: The product search query.
                domain: Walmart domain.
                device: Device profile: desktop or mobile.
                sort_by: Sort order for results.
                start_page: First page to return.
                min_price: Minimum price filter.
                max_price: Maximum price filter.
                fulfillment_speed: Fulfillment speed filter.
                fulfillment_type: Fulfillment type filter.
                delivery_zip: Delivery ZIP/postal code.
                store_id: Restrict to a store id.
            """
            _p = {"query": query, "domain": domain, "device": device, "sort_by": sort_by, "start_page": start_page, "min_price": min_price, "max_price": max_price, "fulfillment_speed": fulfillment_speed, "fulfillment_type": fulfillment_type, "delivery_zip": delivery_zip, "store_id": store_id}
            return _run(lambda: client.walmart.search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_walmart_search)
        @function_tool
        def scavio_walmart_product(product_id: str, domain: Optional[str] = None, device: Optional[str] = None, delivery_zip: Optional[str] = None, store_id: Optional[str] = None) -> dict:
            """Fetch full Walmart product details by product id.

            Args:
                product_id: Walmart product id.
                domain: Walmart domain.
                device: Device profile: desktop or mobile.
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
                sort_by: Sort order for results.
                cursor: Pagination cursor.
            """
            _p = {"query": query, "sort_by": sort_by, "cursor": cursor}
            return _run(lambda: client.youtube.shorts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_shorts)
        @function_tool
        def scavio_youtube_suggestions(query: str, language: Optional[str] = None, region: Optional[str] = None) -> dict:
            """Fetch YouTube search autocomplete suggestions for a query.

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
            """Fetch full details for a YouTube video (title, author, view count, description, captions, chapters).

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
            """List comments on a YouTube video.

            Args:
                video_id: YouTube video id or a full watch URL.
                cursor: Pagination cursor.
            """
            _p = {"video_id": video_id, "cursor": cursor}
            return _run(lambda: client.youtube.comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_comments)
        @function_tool
        def scavio_youtube_comment_replies(video_id: str, reply_cursor: str, cursor: Optional[str] = None) -> dict:
            """List replies to a YouTube comment.

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
            """Fetch a YouTube video's transcript or timed subtitles. Costs 8 credits.

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
            """List videos related to a YouTube video.

            Args:
                video_id: YouTube video id or a full watch URL.
                cursor: Pagination cursor.
            """
            _p = {"video_id": video_id, "cursor": cursor}
            return _run(lambda: client.youtube.related(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_related)
        @function_tool
        def scavio_youtube_channel_search(query: str, cursor: Optional[str] = None) -> dict:
            """Search YouTube channels by keyword.

            Args:
                query: The channel search query.
                cursor: Pagination cursor.
            """
            _p = {"query": query, "cursor": cursor}
            return _run(lambda: client.youtube.channel_search(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_search)
        @function_tool
        def scavio_youtube_channel(channel_id: str) -> dict:
            """Fetch a YouTube channel's details (subscribers, video count, views, links).

            Args:
                channel_id: YouTube channel id, @handle, or channel URL.
            """
            _p = {"channel_id": channel_id}
            return _run(lambda: client.youtube.channel(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel)
        @function_tool
        def scavio_youtube_channel_videos(channel_id: str, cursor: Optional[str] = None) -> dict:
            """List a YouTube channel's uploaded videos.

            Args:
                channel_id: YouTube channel id.
                cursor: Pagination cursor.
            """
            _p = {"channel_id": channel_id, "cursor": cursor}
            return _run(lambda: client.youtube.channel_videos(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_videos)
        @function_tool
        def scavio_youtube_channel_shorts(channel_id: str, cursor: Optional[str] = None) -> dict:
            """List a YouTube channel's Shorts.

            Args:
                channel_id: YouTube channel id.
                cursor: Pagination cursor.
            """
            _p = {"channel_id": channel_id, "cursor": cursor}
            return _run(lambda: client.youtube.channel_shorts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_shorts)
        @function_tool
        def scavio_youtube_channel_community(channel_id: str, cursor: Optional[str] = None) -> dict:
            """List a YouTube channel's community posts.

            Args:
                channel_id: YouTube channel id.
                cursor: Pagination cursor.
            """
            _p = {"channel_id": channel_id, "cursor": cursor}
            return _run(lambda: client.youtube.channel_community(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_youtube_channel_community)
        @function_tool
        def scavio_youtube_channel_resolve(channel: str) -> dict:
            """Resolve a YouTube @handle or channel URL to a channel id.

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
        def scavio_reddit_post(url: str) -> dict:
            """Fetch one Reddit post by URL. Costs 1 credit. data is a flat post object (title, text, score, upvote_ratio, num_comments, subreddit, author) and carries no comments.

            Args:
                url: Full URL of the Reddit post.
            """
            _p = {"url": url}
            return _run(lambda: client.reddit.post(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_reddit_post)

    if all or enable_tiktok:
        @function_tool
        def scavio_tiktok_profile(username: Optional[str] = None, sec_user_id: Optional[str] = None) -> dict:
            """Fetch a TikTok user profile by username or secUid.

            Args:
                username: TikTok username (without @). Provide this or sec_user_id.
                sec_user_id: TikTok secUid. Provide this or username.
            """
            _p = {"username": username, "sec_user_id": sec_user_id}
            return _run(lambda: client.tiktok.profile(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_profile)
        @function_tool
        def scavio_tiktok_user_posts(sec_user_id: str, cursor: Optional[str] = None, count: Optional[int] = None, sort_type: Optional[str] = None) -> dict:
            """List a TikTok user's posts by secUid.

            Args:
                sec_user_id: TikTok secUid of the user.
                cursor: Pagination cursor.
                count: Number of posts to return.
                sort_type: Sort order for posts.
            """
            _p = {"sec_user_id": sec_user_id, "cursor": cursor, "count": count, "sort_type": sort_type}
            return _run(lambda: client.tiktok.user_posts(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_user_posts)
        @function_tool
        def scavio_tiktok_video(video_id: str) -> dict:
            """Fetch a TikTok video by id.

            Args:
                video_id: TikTok video id.
            """
            _p = {"video_id": video_id}
            return _run(lambda: client.tiktok.video(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_video)
        @function_tool
        def scavio_tiktok_video_comments(video_id: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """List comments on a TikTok video.

            Args:
                video_id: TikTok video id.
                cursor: Pagination cursor.
                count: Number of comments to return.
            """
            _p = {"video_id": video_id, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.video_comments(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_video_comments)
        @function_tool
        def scavio_tiktok_comment_replies(video_id: str, comment_id: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """List replies to a TikTok video comment.

            Args:
                video_id: TikTok video id.
                comment_id: Parent comment id.
                cursor: Pagination cursor.
                count: Number of replies to return.
            """
            _p = {"video_id": video_id, "comment_id": comment_id, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.comment_replies(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_comment_replies)
        @function_tool
        def scavio_tiktok_search_videos(keyword: str, cursor: Optional[str] = None, count: Optional[int] = None, sort_type: Optional[str] = None, publish_time: Optional[str] = None) -> dict:
            """Search TikTok videos by keyword.

            Args:
                keyword: Search keyword.
                cursor: Pagination cursor.
                count: Number of videos to return.
                sort_type: Sort order for results.
                publish_time: Publish-time filter.
            """
            _p = {"keyword": keyword, "cursor": cursor, "count": count, "sort_type": sort_type, "publish_time": publish_time}
            return _run(lambda: client.tiktok.search_videos(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_search_videos)
        @function_tool
        def scavio_tiktok_search_users(keyword: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """Search TikTok users by keyword.

            Args:
                keyword: Search keyword.
                cursor: Pagination cursor.
                count: Number of users to return.
            """
            _p = {"keyword": keyword, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.search_users(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_search_users)
        @function_tool
        def scavio_tiktok_hashtag(hashtag_name: Optional[str] = None, hashtag_id: Optional[str] = None) -> dict:
            """Fetch a TikTok hashtag by name or id.

            Args:
                hashtag_name: Hashtag name (without #). Provide this or hashtag_id.
                hashtag_id: Hashtag id. Provide this or hashtag_name.
            """
            _p = {"hashtag_name": hashtag_name, "hashtag_id": hashtag_id}
            return _run(lambda: client.tiktok.hashtag(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_hashtag)
        @function_tool
        def scavio_tiktok_hashtag_videos(hashtag_id: str, cursor: Optional[str] = None, count: Optional[int] = None) -> dict:
            """List videos for a TikTok hashtag by id.

            Args:
                hashtag_id: Hashtag id.
                cursor: Pagination cursor.
                count: Number of videos to return.
            """
            _p = {"hashtag_id": hashtag_id, "cursor": cursor, "count": count}
            return _run(lambda: client.tiktok.hashtag_videos(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_hashtag_videos)
        @function_tool
        def scavio_tiktok_user_followers(sec_user_id: str, count: Optional[int] = None, page_token: Optional[str] = None, min_time: Optional[int] = None) -> dict:
            """List a TikTok user's followers by secUid.

            Args:
                sec_user_id: TikTok secUid of the user.
                count: Number of followers to return.
                page_token: Pagination token.
                min_time: Minimum timestamp filter.
            """
            _p = {"sec_user_id": sec_user_id, "count": count, "page_token": page_token, "min_time": min_time}
            return _run(lambda: client.tiktok.user_followers(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_user_followers)
        @function_tool
        def scavio_tiktok_user_followings(sec_user_id: str, count: Optional[int] = None, page_token: Optional[str] = None, min_time: Optional[int] = None) -> dict:
            """List the accounts a TikTok user follows, by secUid.

            Args:
                sec_user_id: TikTok secUid of the user.
                count: Number of followings to return.
                page_token: Pagination token.
                min_time: Minimum timestamp filter.
            """
            _p = {"sec_user_id": sec_user_id, "count": count, "page_token": page_token, "min_time": min_time}
            return _run(lambda: client.tiktok.user_followings(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_tiktok_user_followings)

    if all or enable_instagram:
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
            """List an Instagram user's posts. Costs 2 credits.

            Args:
                username: Instagram username. Provide this or user_id.
                user_id: Instagram user id. Provide this or username.
                count: Number of posts to return.
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
                count: Number of reels to return.
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
                count: Number of tagged posts to return.
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
            """Fetch an Instagram post by URL, media id, or shortcode. Costs 8 credits.

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
                sort_order: Comment sort order.
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
                count: Number of followers to return.
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
                count: Number of followings to return.
                cursor: Pagination cursor.
            """
            _p = {"username": username, "user_id": user_id, "count": count, "cursor": cursor}
            return _run(lambda: client.instagram.user_followings(**{k: v for k, v in _p.items() if v is not None}))
        tools.append(scavio_instagram_user_followings)

    return tools
