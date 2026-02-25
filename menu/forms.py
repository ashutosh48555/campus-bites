from django import forms
from .models import MenuItem, Category


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'price', 'is_available', 'preparation_time_minutes', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent', 'placeholder': 'e.g., Cappuccino'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent', 'rows': 3, 'placeholder': 'Brief description of the item'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent', 'placeholder': '0.00', 'step': '0.01'}),
            'preparation_time_minutes': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent', 'placeholder': '5'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-amber-600 focus:ring-amber-500 border-gray-300 rounded'}),
            'image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent'})
        }

    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        if shop:
            self.fields['category'].queryset = Category.objects.filter(shop=shop)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent', 'placeholder': 'e.g., Beverages, Snacks, Meals'})
        }
