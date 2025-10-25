from django import forms
from .models import Invoice, InvoiceItem, LetterHead

class LetterHeadForm(forms.ModelForm):
    class Meta:
        model = LetterHead
        fields = ['name', 'image']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['document_type', 'letterhead', 'customer_name', 'address', 'date', 'note']
        widgets = {
            'document_type': forms.RadioSelect(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note'].initial = """1. Payment: 50% advance with order, balance before delivery
2. Delivery Period: 4-5 weeks from the date of order confirmation
3. GST Extra as applicable
4. Validity: This quotation is valid for 30 days
5. Installation charges extra if required"""

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['srno', 'description', 'quantity', 'length', 'breadth', 'area', 'unit_price']
        widgets = {
            'srno': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'resize: vertical;'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'breadth': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

InvoiceItemFormSet = forms.inlineformset_factory(
    Invoice, 
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True
)