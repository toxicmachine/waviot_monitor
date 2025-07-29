from django import forms


class DeviceSearchForm(forms.Form):
    device_search_field = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control me-2',
                                                                        'placeholder': 'Введите номер прибора учета...',
                                                                        'autofocus': 'true',
                                                                        'id': 'search_input',
                                                                        'required': 'True',
                                                                        'pattern': "[0-9]*",
                                                                        'type': "number",
                                                                        }),
                                          max_length=20,
                                          label=False,
                                          required=False,)


class AddressSearchForm(forms.Form):
    address_search_field = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control me-2',
                                                                         'placeholder': 'Введите ФИАС строения или адрес строения...',
                                                                         'autofocus': 'true',
                                                                         'id': 'search_input',
                                                                         'required': 'True',
                                                                         }),
                                           max_length=200,
                                           label=False,
                                           required=False,)


class FileUploadForm(forms.Form):
    file_field = forms.FileField(label='Выберите файл:',
                                 widget=forms.ClearableFileInput(
                                     attrs={'class': "form-control",
                                            'id': "inputFile",
                                            },
                                 ),
                                 )