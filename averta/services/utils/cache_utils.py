"""
Cache utilities for page-level caching and cache invalidation.
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
# from django.utils.cache import get_cache_key
import hashlib
# import json


def generate_cache_key(prefix, *args, **kwargs):
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix: Cache key prefix (e.g., 'page_home', 'query_services')
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key (None values are skipped)
    
    Returns:
        str: Generated cache key
    """
    # Filter out None values from kwargs for consistent key generation
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    # Sort kwargs for consistent key generation
    sorted_kwargs = sorted(filtered_kwargs.items())
    
    # Create a string representation of all arguments
    # Handle different types properly
    def safe_str(val):
        if val is None:
            return 'None'
        elif isinstance(val, (list, tuple)):
            return ','.join(str(item) for item in val)
        elif isinstance(val, dict):
            return ','.join(f"{k}:{v}" for k, v in sorted(val.items()))
        else:
            return str(val)
    
    key_parts = [prefix] + [safe_str(arg) for arg in args] + [f"{k}={safe_str(v)}" for k, v in sorted_kwargs]
    key_string = "|".join(key_parts)
    
    # Hash the key if it's too long (Django cache keys have length limits)
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
        return f"ganaqro:{prefix}:{key_string}"
    
    return f"ganaqro:{key_string}"


def get_page_cache_key(view_name, lang, **query_params):
    """
    Generate cache key for a page view.
    
    Args:
        view_name: Name of the view (e.g., 'home', 'project-list')
        lang: Language code
        **query_params: Query parameters from request.GET
    
    Returns:
        str: Cache key for the page
    """
    # Sort query params for consistent keys
    sorted_params = sorted(query_params.items())
    return generate_cache_key(f"page_{view_name}", lang, **dict(sorted_params))


def bump_cache_version():
    """Increment global cache version so versioned keys miss stale entries."""
    try:
        current_version = cache.get('cache_version', 0) or 0
        cache.set('cache_version', current_version + 1, None)
    except Exception:
        try:
            cache.clear()
        except Exception:
            pass


def get_cache_version_token():
    """
    Token embedded in cache keys: invalidation counter + deploy schema version.
    Changing CACHE_SCHEMA_VERSION in settings invalidates all cached entries.
    """
    try:
        invalidation_version = cache.get('cache_version', 0) or 0
    except Exception:
        invalidation_version = 0
    schema_version = getattr(settings, 'CACHE_SCHEMA_VERSION', 1)
    return f'{invalidation_version}:{schema_version}'


def get_query_cache_key(query_name, *args, **kwargs):
    """
    Generate cache key for a database query.
    
    Args:
        query_name: Name of the query function (e.g., 'services', 'about')
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        str: Cache key for the query
    """
    return generate_cache_key(f"query_{query_name}", *args, **kwargs)


def cached_query(timeout=None):
    """
    Decorator to cache the result of a query function.
    
    Args:
        timeout: Cache timeout in seconds, callable function, or None (uses CACHE_TIMEOUT_MEDIUM).
                 Can also be string like 'CACHE_TIMEOUT_LONG' to read from settings.
    
    Usage:
        @cached_query(timeout=300)
        @cached_query(timeout=getattr(settings, 'CACHE_TIMEOUT_LONG', 3600))
        def get_services(lang='az', is_active=True):
            ...
    """
    # If timeout is a string, it's a settings attribute name
    timeout_settings_key = None
    if isinstance(timeout, str):
        timeout_settings_key = timeout
        timeout = None
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get timeout value - handle all cases
            try:
                if timeout_settings_key:
                    # Read from settings dynamically
                    cache_timeout = getattr(settings, timeout_settings_key, getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300))
                elif callable(timeout):
                    # Callable function (e.g., lambda)
                    cache_timeout = timeout()
                elif timeout is None:
                    # Default timeout from settings
                    cache_timeout = getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)
                else:
                    # Fixed timeout value
                    cache_timeout = int(timeout)
            except Exception:
                # Fallback to default timeout if any error
                cache_timeout = getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)
            
            # Generate cache key from function name and arguments
            # Include cache version for invalidation support
            cache_version = get_cache_version_token()

            # Generate cache key with all parameters
            try:
                cache_key = get_query_cache_key(
                    func.__name__, 
                    *args, 
                    cache_version=cache_version,
                    **kwargs
                )
            except Exception as e:
                # If key generation fails, skip caching
                return func(*args, **kwargs)
            
            # Try to get from cache
            try:
                result = cache.get(cache_key)
                if result is not None:
                    return result
            except Exception:
                # If cache read fails, continue without cache
                pass
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                # Cache result (including None values, but with shorter timeout)
                try:
                    if result is None:
                        # Cache None values with shorter timeout
                        cache.set(cache_key, result, min(cache_timeout, 60))
                    else:
                        # Cache actual values with full timeout
                        cache.set(cache_key, result, cache_timeout)
                except Exception:
                    # If cache write fails, just return result without caching
                    pass
                return result
            except Exception as e:
                # If function fails, don't cache the error, just raise it
                raise
        return wrapper
    return decorator


def invalidate_page_cache(view_names=None):
    """
    Invalidate cache for specific pages or all pages.
    
    Args:
        view_names: List of view names to invalidate. If None, invalidates all pages.
    """
    if view_names is None:
        try:
            cache.clear()
        except Exception:
            pass
    else:
        bump_cache_version()


def invalidate_query_cache(query_names=None):
    """
    Invalidate cache for specific queries or all queries.
    
    Args:
        query_names: List of query names to invalidate. If None, invalidates all queries.
    """
    bump_cache_version()


def cached_page_data(timeout=None):
    """
    Decorator to cache page data functions (like get_home_page_data, get_project_list_data).
    
    Args:
        timeout: Cache timeout in seconds, callable function, or None (uses CACHE_TIMEOUT_MEDIUM).
                 Can also be string like 'CACHE_TIMEOUT_MEDIUM' to read from settings.
    
    Usage:
        @cached_page_data(timeout=300)
        @cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
        def get_home_page_data(request, lang):
            ...
    """
    # If timeout is a string, it's a settings attribute name
    timeout_settings_key = None
    if isinstance(timeout, str):
        timeout_settings_key = timeout
        timeout = None
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, lang, *args, **kwargs):
            # Get timeout value - handle all cases
            try:
                if timeout_settings_key:
                    # Read from settings dynamically
                    cache_timeout = getattr(settings, timeout_settings_key, getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300))
                elif callable(timeout):
                    # Callable function (e.g., lambda)
                    cache_timeout = timeout()
                elif timeout is None:
                    # Default timeout from settings
                    cache_timeout = getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)
                else:
                    # Fixed timeout value
                    cache_timeout = int(timeout)
            except Exception:
                # Fallback to default timeout if any error
                cache_timeout = getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)
            
            # Generate cache key from function name, language, and query parameters
            # Include cache version for invalidation support
            cache_version = get_cache_version_token()

            try:
                query_params = dict(request.GET.items())
                view_name = func.__name__.replace('get_', '').replace('_data', '')
                cache_key = get_page_cache_key(view_name, lang, cache_version=cache_version, **query_params)
            except Exception:
                # If key generation fails, skip caching
                return func(request, lang, *args, **kwargs)
            
            # Try to get from cache
            try:
                result = cache.get(cache_key)
                if result is not None:
                    return result
            except Exception:
                # If cache read fails, continue without cache
                pass
            
            # Execute function and cache result
            try:
                result = func(request, lang, *args, **kwargs)
                # Always cache result (including None, but with shorter timeout)
                try:
                    if result is None:
                        cache.set(cache_key, result, min(cache_timeout, 60))
                    else:
                        cache.set(cache_key, result, cache_timeout)
                except Exception:
                    # If cache write fails, just return result without caching
                    pass
                return result
            except Exception as e:
                # If function fails, don't cache the error, just raise it
                raise
        return wrapper
    return decorator


def invalidate_model_cache(model_name=None):
    """
    Invalidate all versioned page/query caches (home, lists, about, hero, etc.).

    Args:
        model_name: Optional label for logging; invalidation is global via cache_version.
    """
    bump_cache_version()

