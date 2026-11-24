import re

from django.conf import settings
from django.contrib.staticfiles.views import serve as serve_django_static
from django.http import HttpResponse
from django.urls import path, re_path
from django.views.static import serve

from .urls import urlpatterns as backend_urls


CLINIC = settings.BASE_DIR.parent / "skin_and_you_ui"
SCRAPPER = settings.BASE_DIR.parent / "wescrapper"


def local_content_policy(get_response):
    def middleware(request):
        response = get_response(request)
        response["Content-Security-Policy"] = (
            "default-src 'self'; connect-src 'self'; "
            "script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; font-src 'self' data:; "
            "frame-src 'self' data: blob:; object-src 'self' data: blob:; "
            "form-action 'self'; base-uri 'self'"
        )
        return response

    return middleware


def clinic_index(request):
    html = (CLINIC / "index.html").read_text(encoding="utf-8")
    return HttpResponse(html.replace('"./', '"/'), content_type="text/html; charset=utf-8")


def clinic_script(request):
    script = (CLINIC / "static/js/main.0b6a833c.js").read_bytes()
    script = script.replace(b"https://api.skinandyou.co.in/", b"/")
    script = script.replace(b"https://skinandyou.co.in/", b"/")
    script = script.replace(
        b"https://cdnjs.cloudflare.com/ajax/libs/pdfobject/2.1.1/pdfobject.min.js",
        b"/assets/vendor/pdfobject.min.js",
    )
    # Treatment serializers return a root-relative media URL.
    script = script.replace(b'Qn+""+e.image', b'e.image')
    return HttpResponse(script, content_type="text/javascript; charset=utf-8")


def clinic_styles(request, filename):
    css = (CLINIC / filename).read_bytes()
    css = re.sub(
        rb"""@import\s+url\(\s*["']?https://fonts\.googleapis\.com/[^)]*\)\s*;""",
        b"",
        css,
    )
    return HttpResponse(css, content_type="text/css; charset=utf-8")


def scrapper_index(request):
    html = (SCRAPPER / "index.html").read_text(encoding="utf-8")
    return HttpResponse(html.replace('"/assets/', '"/wescrapper/assets/'))


def scrapper_script(request):
    script = (SCRAPPER / "assets/index-D9rqZkeY.js").read_text(encoding="utf-8")
    script = script.replace('"/assets/', '"/wescrapper/assets/')
    script = script.replace("c.jsx(ON,{children:c.jsxs(MN", 'c.jsx(ON,{basename:"/wescrapper",children:c.jsxs(MN')
    script = script.replace('href:"/",className:"text-blue-500', 'href:"/wescrapper/",className:"text-blue-500')
    script = re.sub(
        r'const s=`Hi WESCRAPPER!.*?nu\.success\("Redirecting to WhatsApp to confirm booking\.\.\."\)',
        """try {
            const bookings = JSON.parse(localStorage.getItem("wescrapper-bookings") || "[]");
            bookings.push({...n, date: kn(e,"yyyy-MM-dd")});
            localStorage.setItem("wescrapper-bookings", JSON.stringify(bookings));
        } catch {
            nu.error("Could not save the pickup request on this device");
            return;
        }
        nu.success("Pickup request saved on this device")""",
        script,
        count=1,
        flags=re.DOTALL,
    )
    script = re.sub(
        r'window\.open\("https://wa\.me/[^"]*","_blank"\)',
        'document.getElementById("contact").querySelector("form").scrollIntoView({behavior:"smooth"})',
        script,
    )
    script = script.replace("Book Pickup Now", "Save pickup request")
    script = script.replace("Chat Now", "Go to pickup form")
    script = script.replace("Quick WhatsApp Booking", "Pickup request form")
    script = script.replace("Schedule online or via WhatsApp in under 2 minutes.", "Enter your pickup details in the form.")
    script = script.replace(
        "Schedule a scrap pickup in minutes. We'll handle the rest.",
        "Save pickup details in this browser. This form does not schedule a pickup.",
    )
    script = script.replace("Chat with us directly for instant booking", "Enter the pickup details you want to save.")
    return HttpResponse(script, content_type="text/javascript; charset=utf-8")


urlpatterns = [
    *backend_urls,
    path("static/js/main.0b6a833c.js", clinic_script),
    re_path(
        r"^(?P<filename>static/css/main\.0d93fe07\.css|assets/css/main-style(?:\+deprecated)?\.css)$",
        clinic_styles,
    ),
    path("assets/<path:path>", serve, {"document_root": CLINIC / "assets"}),
    re_path(r"^static/(?P<path>(?:js|css|media)/.+)$", serve, {"document_root": CLINIC / "static"}),
    path("static/<path:path>", serve_django_static, {"insecure": True}),
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
    path("wescrapper/", scrapper_index),
    path("wescrapper/assets/index-D9rqZkeY.js", scrapper_script),
    path("wescrapper/<path:path>", serve, {"document_root": SCRAPPER}),
    re_path(
        r"^(?P<path>favicon\.ico|manifest\.json|logo(?:192|512)\.png|robots\.txt|header\.png|footer\.jpg)$",
        serve,
        {"document_root": CLINIC},
    ),
    re_path(r"^(?!(?:api|admin|cms|assets|static|media|wescrapper)(?:/|$))[^.]*$", clinic_index),
]
