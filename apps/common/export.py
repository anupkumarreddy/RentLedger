import csv

from django.http import HttpResponse
from django.utils import timezone


def export_csv(filename_stem, header, rows):
    """Return an ``HttpResponse`` streaming a simple CSV download."""
    stamp = timezone.localdate().isoformat()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename_stem}-{stamp}.csv"'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return response
