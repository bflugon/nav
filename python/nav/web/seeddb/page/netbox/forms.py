#
# Copyright (C) 2011, 2012 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""Forms for seeddb netbox view"""
import logging
from socket import error as SocketError

from django import forms
from django_hstore.forms import DictionaryField
from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import (Layout, Row, Column, Submit,
                                            Fieldset, Field)

from nav.web.crispyforms import LabelSubmit, NavButton
from nav.models.manage import Room, Category, Organization, Netbox
from nav.models.manage import NetboxInfo
from nav.web.seeddb.utils.edit import (resolve_ip_and_sysname, does_ip_exist,
                                       does_sysname_exist)

_logger = logging.getLogger(__name__)


class NetboxModelForm(forms.ModelForm):
    """Modelform for netbox for use in SeedDB"""
    ip = forms.CharField()
    serial = forms.CharField(required=False)
    function = forms.CharField(required=False)
    data = DictionaryField(widget=forms.Textarea(), label='Attributes',
                           required=False)

    class Meta(object):
        model = Netbox
        fields = ['ip', 'room', 'category', 'organization',
                  'read_only', 'read_write', 'snmp_version',
                  'netboxgroups', 'sysname', 'type', 'data', 'serial']
        widgets = {
            'sysname': forms.TextInput(attrs={'disabled': True}),
            'type': forms.Select(attrs={'disabled': True}),
            'snmp_version': forms.TextInput(attrs={'disabled': True}),
        }

    def __init__(self, *args, **kwargs):
        super(NetboxModelForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['serial'].initial = self.instance.device.serial
            try:
                netboxinfo = self.instance.info_set.get(variable='function')
            except NetboxInfo.DoesNotExist:
                pass
            else:
                self.fields['function'].initial = netboxinfo.value

        css_class = 'large-4'
        self.helper = FormHelper()
        self.helper.form_action = ''
        self.helper.form_method = 'POST'
        self.helper.form_id = 'seeddb-netbox-form'
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset('Required fields',
                             'ip', 'room', 'category', 'organization'),
                    css_class=css_class),
                Column(
                    Fieldset('SNMP communities',
                             Row(
                                 Column('read_only', css_class='medium-6'),
                                 Column('read_write', css_class='medium-6')
                             ),
                             NavButton('check_connectivity',
                                       'Check connectivity',
                                       css_class='check_connectivity')),
                    Fieldset('Collected info',
                             'sysname', 'snmp_version', 'type', 'serial'),
                    css_class=css_class),
                Column(
                    Fieldset('Meta information',
                             'function',
                             Field('netboxgroups', css_class='select2'),
                             'data'),
                    css_class=css_class),
            ),
            Submit('submit', 'Save IP device')
        )

    def clean_ip(self):
        """Make sure IP-address is valid"""
        name = self.cleaned_data['ip'].strip()
        try:
            ip, _ = resolve_ip_and_sysname(name)
        except SocketError:
            raise forms.ValidationError("Could not resolve name %s" % name)
        return unicode(ip)

    def clean_serial(self):
        """Make sure the serial number is not in use"""
        serial = self.cleaned_data['serial'].strip()
        try:
            netbox_with_serial = Netbox.objects.get(device__serial=serial)
        except Netbox.DoesNotExist:
            return serial
        else:
            if netbox_with_serial != self.instance:
                raise forms.ValidationError(
                    "Serial (%s) is already taken by %s" % (
                        serial, netbox_with_serial))

    def clean(self):
        """Make sure that categories that require communities has that"""
        cleaned_data = self.cleaned_data
        ip = cleaned_data.get('ip')
        cat = cleaned_data.get('category')
        ro_community = cleaned_data.get('read_only')

        if ip:
            try:
                self._check_existing_ip(ip)
            except IPExistsException, ex:
                self._errors['ip'] = self.error_class(ex.message)
                del cleaned_data['ip']

        if cat and cat.req_snmp and not ro_community:
            self._errors['read_only'] = self.error_class(
                ["Category %s requires SNMP access." % cat.id])
            del cleaned_data['category']
            del cleaned_data['read_only']

        return cleaned_data

    def _check_existing_ip(self, ip):
        msg = []
        _, sysname = resolve_ip_and_sysname(ip)
        if does_ip_exist(ip, self.instance.pk):
            msg.append("IP (%s) is already in database" % ip)
        if does_sysname_exist(sysname, self.instance.pk):
            msg.append("Sysname (%s) is already in database" % sysname)
        if len(msg) > 0:
            raise IPExistsException(msg)


class NetboxFilterForm(forms.Form):
    """Form for filtering netboxes on the list page"""
    category = forms.ModelChoiceField(
        Category.objects.order_by('id').all(), required=False)
    room = forms.ModelChoiceField(
        Room.objects.order_by('id').all(), required=False)
    organization = forms.ModelChoiceField(
        Organization.objects.order_by('id').all(), required=False)

    def __init__(self, *args, **kwargs):
        super(NetboxFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = ''
        self.helper.form_method = 'GET'
        self.helper.form_class = 'custom'

        self.helper.layout = Layout(
            Fieldset(
                'Filter devices',
                Row(
                    Column('category', css_class='medium-3'),
                    Column('room', css_class='medium-3'),
                    Column('organization', css_class='medium-3'),
                    Column(LabelSubmit('submit', 'Filter',
                                       css_class='postfix'),
                           css_class='medium-3')
                )
            )
        )


class NetboxMoveForm(forms.Form):
    """Form for moving netboxes to another room and/or organization"""
    room = forms.ModelChoiceField(
        Room.objects.order_by('id').all(), required=False)
    organization = forms.ModelChoiceField(
        Organization.objects.order_by('id').all(), required=False)


class IPExistsException(Exception):
    """Exception raised when a device with the same IP-address exists"""
    pass
