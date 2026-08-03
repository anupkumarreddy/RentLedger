from django import forms


class DateInput(forms.DateInput):
    input_type = "date"


class BaseStyledForm(forms.ModelForm):
    """Base ModelForm.

    Field widgets inherit their look from the global ``input/select/textarea``
    styles in ``main.css``; here we only nudge widget-specific classes that the
    base layer intentionally skips (checkboxes).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault(
                    "class",
                    "size-5 rounded-md border-slate-300 text-brand-600 focus:ring-brand-500/30",
                )
