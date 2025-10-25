from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

class LetterHead(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='letterheads/')
    
    def __str__(self):
        return self.name

class Invoice(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('quotation', 'Quotation'),
        ('invoice', 'Invoice'),
    ]
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='quotation')
    letterhead = models.ForeignKey(LetterHead, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200)
    address = models.TextField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    quotation_number = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.quotation_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice and last_invoice.quotation_number:
                try:
                    last_number = int(last_invoice.quotation_number.split('/')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    next_number = 1
            else:
                next_number = 1
            prefix = 'QUOT' if self.document_type == 'quotation' else 'INV'
            self.quotation_number = f'{prefix}/{timezone.now().year}/{next_number:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        label = 'Quotation' if self.document_type == 'quotation' else 'Invoice'
        return f"{label} {self.quotation_number} - {self.customer_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    srno = models.IntegerField()
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2,default=1)
    length = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    breadth = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.srno:
            # Get the last srno for this invoice
            last_item = InvoiceItem.objects.filter(invoice=self.invoice).order_by('-srno').first()
            self.srno = (last_item.srno + 1) if last_item else 1

        # compute total_amount before saving using special fractional rules for length/breadth
        def convert_fractional(value: Decimal) -> Decimal:
            """
            If value has a fractional part, convert the fractional part according to mapping.
            
            For example:
            12.4 -> The .4 becomes .33
            12.5 -> The .5 becomes .42
            
            Mapping for decimal places:
            .1 -> .08    .6 -> .50
            .2 -> .16    .7 -> .58
            .3 -> .25    .8 -> .66
            .4 -> .33    .9 -> .75
            .5 -> .42    
            """
            try:
                # Normalize to quantize to 2 decimal places for consistent extraction
                q = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except Exception:
                return value

            sign = -1 if q < 0 else 1
            q = abs(q)
            whole = int(q // 1)
            
            # Get the decimal part (e.g., for 12.45 get 0.45)
            decimal_part = q - Decimal(whole)
            
            # Extract the first decimal place (e.g., from 0.45 get 4)
            first_decimal = int((decimal_part * 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            # Mapping for the first decimal place
            mapping = {
                1: Decimal('0.08'),
                2: Decimal('0.16'),
                3: Decimal('0.25'),
                4: Decimal('0.33'),
                5: Decimal('0.42'),
                6: Decimal('0.50'),
                7: Decimal('0.58'),
                8: Decimal('0.66'),
                9: Decimal('0.75'),
                10: Decimal('0.83'),  # No conversion for .0
                11: Decimal('0.92'),
            }
            
            # Convert the decimal part according to the mapping
            converted_decimal = mapping.get(first_decimal, decimal_part)
            
            # Return the whole number plus the converted decimal
            return Decimal(whole) + (converted_decimal * Decimal(sign))

            # Fallback: return original value
            return Decimal(whole) + (Decimal(frac_int) / Decimal(100)) * Decimal(sign)

        try:
            # Use Decimal arithmetic and apply conversion to length and breadth only
            qty = Decimal(self.quantity)
            length = Decimal(self.length)
            breadth = Decimal(self.breadth)
            unit = Decimal(self.unit_price)

            conv_length = convert_fractional(length)
            conv_breadth = convert_fractional(breadth)

                # Calculate area using converted measurements (qty * conv_length * conv_breadth)
            self.area = (qty * conv_length * conv_breadth).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
                # Calculate total amount using the area and unit price
            self.total_amount = (self.area * unit).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            self.area = None
            self.total_amount = None
        super().save(*args, **kwargs)
    
    @property
    def total(self):
        # prefer stored total_amount, fallback to computing on the fly
        if self.total_amount is not None:
            return self.total_amount
        return self.quantity * self.length * self.breadth * self.unit_price
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"